from copy import copy
from django.shortcuts import render, redirect  # render error pages
from nested_lookup import nested_lookup
from propay_api import config
import base64
import json
import logging
import pdb # debugging
import requests  # for json to use Propay API


"""
Documentation found in "ProtectPay-API-Manual-REST.pdf"

* default request format:
    --- request.GET ---
    {
        'rname': 'get_payerId_details',    # specify name of request (eg. "get_payerId_details"),
        'args': {
            'identifier': '65396',
        }
    }

    --- request.POST ---
    ** handles both POST and PUT requests


NOTE: some api calls require a sub dictionary to be sent along with the rest of
the arguments in order to work properly.  Check REST api call examples in propay
docs to check if a function needs that or not.

"""
infologger = logging.getLogger("propay")
debuglogger = logging.getLogger("propay.debug")

# ------------------------------------------------------------------------------
def helper_log_call(fname, result, **kwargs):
    """
    helper function to log api call and any non-sensitive info that may be helpful
    to know

    called at the end of each api call function so result is known as well.
    """
    loggable_keys = [
        'PayerAccountId', 'PaymentMethodID', 'Name',
        'ExternalId1', 'TransactionHistoryId',
    ]

    log_string = f"propayapi ({fname}) kwargs=" + "{"
    for key in loggable_keys:
        if key in kwargs:
            log_string += f"{key}: {kwargs[key]}, "

    log_string += "}"
    if 'ResultValue' in result:
        log_string += f" result: {result['ResultValue']}"

    elif 'RequestResult' in result:
        log_string += f" result: {result['RequestResult']}"

    else:
        log_string += f" result: {result}"

    infologger.info(log_string)


def helper_set_auth(authoverride) -> set:
    """
    auth can be a tuple passed in of (BILLER_ID, AUTH_TOKEN)
    otherwise default is whatever is in the config file
    """
    if authoverride:
        return tuple(authoverride)
    else:
        return (config.BILLER_ID, config.AUTH_TOKEN)


def helper_set_baseuri(urioverride) -> str:
    """
    determine baseuri
    """
    if urioverride:
        return urioverride
    else:
        return config.PROTECTPAY_BASE_URI

# -------------------------------- PROPAY_API ----------------------------------
def hosted_transaction(request, return_url, account, plan):
    # this will work with the normal api uri and credentials, but not the testing one?
    """
    calls the propay processes needed to create a propay session, process/store card

    account.ccard1
    account.transid
    account.price_code
    account.accttype
    account.authcode
    account.areacode1

    """

    if account.payer_account_id is None:
        r2 = requests.put(
            # doc 5.1: Create a Payer
            config.PROTECTPAY_PAYER_API,
            auth=(config.BILLER_ID, config.AUTH_TOKEN),
            # json={"Name":account.first_name +" "+ account.last_name,"Email":account.email,"ExternalID1":account.token},
            json={"Name": account.first_name + " " + \
                  account.last_name, "ExternalID1": account.token},
        )

        if r2.json()['RequestResult']['ResultCode'] != '00':
            # --- couldn't authenticate, send to error page saying so ---
            pass

        # --- authenification passed, now redirect user to payment page ---
        PayerAccountId = r2.json()['ExternalAccountID']
        account.payer_account_id = r2.json()['ExternalAccountID']
        account.save()

    transaction_data = {
        # "BillerAccountID" => env('BILLER_ID'),
        # "AuthorizationToken" : env('AUTH_TOKEN'),
        "PayerAccountId": account.payer_account_id,
        # "MerchantProfileId" : '2305383',
        "MerchantProfileId": config.MERCHANT_PROFILE_ID,  # ? faxpipe profile id ?
        "Amount": plan['propay'],
        "CurrencyCode": "USD",
        "InvoiceNumber": "Account Signup",
        # "InvoiceNumber" : $decoded['HostedTransactionIdentifier'];
        "Comment1": plan['description'],
        "CardHolderNameRequirementType": 1,
        "SecurityCodeRequirementType": 1,
        "AvsRequirementType": 1,
        # "AuthOnly" : False,
        # "ProcessCard" : True,
        "StoreCard": True,
        "OnlyStoreCardOnSuccessfulProcess": False,
        "CssUrl": config.CSS_URL,
        "Address1": account.address,
        "Address2": '',
        "City": account.city,
        "Country": 'USA',
        "Description": '',
        "Name": account.first_name + ' ' + account.last_name,
        "State": account.state,
        "ZipCode": account.zip,
        "BillerIdentityId": None,
        "CreationDate": None,
        "HostedTransactionIdentifier": None,
        # ?? key ??
        "ReturnURL": return_url,
        "PaymentTypeId": "0",
        "Protected": False
    }

    if plan['type'] == 0:
        # --- plan zero, don't charge but take card ---
        transaction_data["AuthOnly"] = True
        transaction_data["ProcessCard"] = False
        transaction_data["InvoiceNumber"] = "Card Authorization"
    else:
        # --- regular signup ---
        transaction_data["AuthOnly"] = False
        transaction_data["ProcessCard"] = True
        transaction_data["OnlyStoreCardOnSuccessfulProcess"] = True

    # ---- create hosted transaction identifier ----
    r3 = requests.put(
        # doc 10.2: Create Hosted Transaction Instance
        config.PROTECTPAY_TRANSACTION_API,
        auth=(config.BILLER_ID, config.AUTH_TOKEN),
        json=transaction_data,
    )

    if r3.json()['Result']['ResultCode'] != '00':
        # --- couldn't authenticate, send to error page saying so ---
        message = "we were unable to authorize a transaction at this time, please notify support"
        return render(request, 'errorpage.html', {"errormessage": message})
        # pass

    account.hostedtransactionidentifier = r3.json()[
                                                  'HostedTransactionIdentifier']
    account.save()

    # ---- go to hosted payment page (hpp) ----
    # return redirect(env('API_URL') . $decoded['HostedTransactionIdentifier']);
    api_url = config.PROTECTPAY_PAYMENT_URL + account.hostedtransactionidentifier

    return redirect(api_url)

# ---------------------------- GET_TRANSACTION_DATA ----------------------------
def get_transaction_info(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    connect to propay api to get info on specified transaction.
    first parameter is uri: 'https://api.propay.com/protectpay/HostedTransactionResults/'
        + the transaction identifier saved in the account model.

    only other thing needed is verification info
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    transId = kwargs['HostedTransactionId']
    uri = f"{baseuri}/HostedTransactionResults/{transId}/"

    resp = requests.get(
        uri,
        auth=auth,
    )

    return resp.json()

# --------------------------- AUTHORIZE TRANSACTION ----------------------------
def put_authorize_transaction(authoverride=None, urioverride=None, **kwargs) -> dict:
    # --- 'IsRecurringPayment' default to false ---
    default_args = {
        'IsRecurringPayment': False,
        'CurrencyCode': 'USD',
        'MerchantProfileId': config.MERCHANT_PROFILE_ID,
        'AuthOnly': True,
        'ProcessCard': False,
        'InvoiceNumber': 'Card Authorization',
    }
    default_args_copy = copy(default_args)

    # --- remove default args if they're in kwargs ---
    for key in default_args_copy:
        if key in kwargs:
            default_args.pop(key)

    kwargs = {**kwargs, **default_args}

    json_data = {
        'Amount': kwargs['Amount'],
        'AuthOnly': kwargs['AuthOnly'],
        'ProcessCard': kwargs['ProcessCard'],
        'InvoiceNumber': kwargs['InvoiceNumber'],
        'CurrencyCode': kwargs['CurrencyCode'],
        'MerchantProfileId': kwargs['MerchantProfileId'],
        'PayerAccountId': kwargs['PayerAccountId'],
        'PaymentMethodID': kwargs['PaymentMethodID'],
        'IsRecurringPayment': kwargs['IsRecurringPayment'],
    }

    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}/Payers/"
    uri += f"{kwargs['PayerAccountId']}/PaymentMethods/AuthorizedTransactions/"

    resp = requests.put(
        uri,
        auth=auth,
        json=json_data,
    )

    resp_json = resp.json()
    helper_log_call("put_authorize_transaction", resp_json, **kwargs)

    return resp.json()

# ---------------------------- CAPTURE TRANSACTION -----------------------------
def put_capture_transaction(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    capture a previously authorized transaction
    """
    if 'MerchantProfileId' in kwargs:
        mpid = kwargs['MerchantProfileId']
    else:
        mpid = config.MERCHANT_PROFILE_ID

    json_data = {
        "CurrencyCode": "USD",
        "MerchantProfileId": mpid,
        "TransactionHistoryId": kwargs["TransactionHistoryId"],
        "Amount": kwargs["Amount"],
        "Comment1": "voiding TransactionHistoryId " + str(kwargs['TransactionHistoryId']),
    }

    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}CapturedTransactions/"
    resp = requests.put(
        uri,
        auth=auth,
        json=json_data,
    )

    resp_json = resp.json()
    helper_log_call("put_capture_transaction", resp_json, **kwargs)

    return resp.json()


# ------------------------------ VOID_TRANSACTION ------------------------------
def put_void_transaction(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    connect to propay api and void a transaction that was placed for the given account
    """
    if 'MerchantProfileId' in kwargs:
        mpid = kwargs['MerchantProfileId']
    else:
        mpid = config.MERCHANT_PROFILE_ID

    json_data = {
        "MerchantProfileId": mpid,
    }
    # --- function requires one or both of TransactionHistoryId and OriginalTransactionId ---
    # if both are sent propay will only use the TransactionHistoryId
    if "TransactionHistoryId" in kwargs:
        json_data['TransactionHistoryId'] = kwargs['TransactionHistoryId']
        json_data["Comment1"] = "voiding TransactionHistoryId " + str(kwargs['TransactionHistoryId'])

    if "OriginalTransactionId" in kwargs:
        json_data['OriginalTransactionId'] = kwargs['OriginalTransactionId']
        json_data["Comment2"] = "voiding OriginalTransactionId " + str(kwargs['OriginalTransactionId'])

    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}VoidedTransactions/"
    resp = requests.put(
        uri,
        auth=auth,
        json=json_data,
    )

    resp_json = resp.json()
    helper_log_call("put_void_transaction", resp_json, **kwargs)

    return resp.json()


# ------------------------------- VALIDATE CARD --------------------------------
def put_validate_card(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    authorize and then void a transaction.  if both steps are successful then
    the card is validated sucessfully.

    if authorization works but voiding doesn't then in theory the card is valid,
    though it is ideal to void that transaction so the payer funds are released.
    uses:
        - put_authorize_transaction
        - put_void_transaction
    """
    PayerAccountId = kwargs['PayerAccountId']
    PaymentMethodID = kwargs['PaymentMethodID']
    # --- authorise transaction for $1 ---
    kwargs['Amount'] = "100"

    authinf = put_authorize_transaction(authoverride, urioverride, **kwargs)
    TransId = nested_lookup('TransactionHistoryId', authinf)

    # --- make sure transid is present and that result code was returned ---
    rmessage = None
    rvalue = "ERROR"
    try:
        authstatus = authinf['Transaction']['ResultCode']['ResultValue']
        if authstatus == "SUCCESS" and len(TransId) > 0:
            TransId = TransId[0]

        else:
            raise KeyError

    except KeyError:
        # --- return early, no transaction found or not successful ---
        return {
            "ResultValue": rvalue,
            "ResultMessage": rmessage,
            "TransactionHistoryId": TransId,
            "AuthorizedTransaction": authinf,
            "VoidedTransaction": None,
        }

    kwargs = {**kwargs, **{'TransactionHistoryId': TransId}}

    # --- if valid then void transaction ---
    voidinf = put_void_transaction(authoverride, urioverride, **kwargs)

    try:
        rvalue = voidinf['Transaction']['ResultCode']['ResultValue']
        rmessage = voidinf['Transaction']['ResultCode']['ResultMessage']

    except Exception as e:
        rmessage = e

    # --- @return info from both calls ---
    rinfo = {
        'ResultValue': rvalue,
        'ResultMessage': rmessage,
        "TransactionHistoryId": TransId,
        'AuthorizedTransaction': authinf,
        'VoidedTransaction': voidinf,
    }
    # no need to log this response, authorize and void calls do on their own
    return rinfo

# ------------------------------ CREATE NEW PAYER ------------------------------
def put_create_payer(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    NOTE: does not check for an existing payer with given arguments.  Will create
    duplicate

    see ProtectPay-API-Manual-REST: section 5.1
    @kwargs:
        required: Name
        optional: EmailAddress, ExternalId1, ExternalId2

    SAMPLE JSON RESPONSE DATA
    resp.json() = {
         "ExternalAccountID":"################",
         "RequestResult": {
             "ResultValue":"SUCCESS",
             "ResultCode":"00",
             "ResultMessage":""
        }
    }
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/"
    resp = requests.put(
        uri,
        auth=auth,
        json=kwargs,
    )

    resp_json = resp.json()
    helper_log_call("put_create_payer", resp_json, **kwargs)

    return resp.json()


# ---------------------------------- ADD CARD ----------------------------------
def put_create_paymentMethod(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    see section 6.1 of ProtectPay-API-Manual-REST
    @kwargs:
        see propay docs or FUNCTION_DICT for required/optional args

    NOTE:
        'BillingInformation' has to be a sub dictionary
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/{kwargs['PayerAccountId']}/PaymentMethods/"
    resp = requests.put(
        uri,
        auth=auth,
        json=kwargs,
    )

    resp_json = resp.json()
    helper_log_call("put_create_paymentMethod", resp_json, **kwargs)

    return resp.json()

# -------------------------------- UPDATE_PAYER --------------------------------
def post_update_payer(authoverride=None, urioverride=None, **kwargs) -> dict:
    """

    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/{kwargs['PayerAccountId']}/"
    resp = requests.post(
        uri,
        auth=auth,
        json=kwargs,
    )

    resp_json = resp.json()
    helper_log_call("post_update_payer", resp_json, **kwargs)

    return resp.json()

# ------------------------------ UPDATE PAYMETHOD ------------------------------
def post_update_paymentMethod(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    see section 6.3 of ProtectPay-API-Manual-REST
    @kwargs:
        see propay docs or FUNCTION_DICT for required/optional args

    NOTE:
        'BillingInformation' has to be a sub dictionary
        this overwrites preexisting info on the card.  So if a field is missing
        that is then turned empty (eg. ZipCode not included will turn it to '')
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/{kwargs['PayerAccountId']}/"
    uri += f"PaymentMethods/{kwargs['PaymentMethodID']}/"
    resp = requests.post(
        uri,
        auth=auth,
        json=kwargs,
    )

    resp_json = resp.json()
    helper_log_call("post_update_paymentMethod", resp_json, **kwargs)

    return resp.json()

# ------------------------------- GET PAYER INFO -------------------------------
def get_payerId_details(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    - combines all kwargs into single query string, any matches will return
    results so combined matches make the resulting response even larger (multiple
    payers)
    - invalid fields don't matter so long as one valid field is requested:
        can search three identifiers:
            - externalId1
            - externalId2
            - name

    EXAMPLE RESPONSE:
    {
        'Payers': [{
            'ExternalId1': '12345',
            'ExternalId2': 'Testaccount12',
            'Name': 'Test Account',
            'PayerAccountId': '################'
        }],
        'RequestResult': {
            'ResultCode': '00',
            'ResultMessage': '',
            'ResultValue': 'SUCCESS'
        }
    }
    """

    query = "?"    # ex: ?&name=Jake Barker&externalId1=65306"
    for key in kwargs:
        query += f"&{key}={kwargs[key]}"

    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/"
    resp = requests.get(
        uri + query,
        auth=auth,
    )

    return resp.json()


# ------------------------- GET PAYMENT METHOD DETIALS -------------------------
def get_paymentMethod_details(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    requests payment method details for given PayerAccountId

    EXAMPLE RESPONSE:
        {
            'RequestResult': {
                'ResultValue': 'SUCCESS',
                'ResultCode': '00',
                'ResultMessage': ''
            },
            'Payers': [
                ### payer info here
            ]
        }
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/{kwargs['PayerAccountId']}/PaymentMethods/"
    resp = requests.get(
        uri,
        auth=auth,
    )

    return resp.json()


# -------------------------------- DELETE PAYER --------------------------------
def delete_PayerAccountId(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    connect to propay api and delete payer with given PayerAccountId
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/{kwargs['PayerAccountId']}/"
    resp = requests.delete(
        uri,
        auth=auth,
    )

    resp_json = resp.json()
    helper_log_call("delete_PayerAccountId", resp_json, **kwargs)

    return resp.json()


# --------------------------- DELETE PAYMENT METHOD ----------------------------
def delete_payMethod(authoverride=None, urioverride=None, **kwargs) -> dict:
    """
    connect to propay api and delete payer with given PayerAccountId
    """
    auth = helper_set_auth(authoverride)
    baseuri = helper_set_baseuri(urioverride)
    uri = f"{baseuri}Payers/{kwargs['PayerAccountId']}/"
    uri += f"PaymentMethods/{kwargs['PaymentMethodID']}/"
    resp = requests.delete(
        uri,
        auth=auth,
    )

    resp_json = resp.json()
    helper_log_call("delete_payMethod", resp_json, **kwargs)

    return resp.json()


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

# function calls and their requirements, used when routing from http request
FUNCTION_DICT = {
    # --- get payment method details ---
    'get_paymentMethod_details': {
        'required': ['PayerAccountId'],
        'optional': [],
        'function': get_paymentMethod_details,
    },
    # --- get payer id details
    'get_payerId_details': {
        'required': [], #combines different query items from propay api
        'optional': ['Name', 'EmailAddress', 'ExternalId1', 'ExternalId2'],
        'function': get_payerId_details,
    },
    'get_transaction_info': {
        'required': ['HostedTransactionId'],
        'optional': [],
        'function': get_transaction_info,
    },
    # --- create payer ---
    'put_create_payer': {
        'required': ['Name'],
        'optional': ['EmailAddress', 'ExternalId1', 'ExternalId2'],
        'function': put_create_payer,
    },
    # --- create payment method ---
    'put_create_paymentMethod': {
        'required': [
            'AccountNumber', 'Description',
            'PayerAccountId', 'PaymentMethodType'
        ],
        'optional': [
            'AccountCountryCode', 'AccountName', 'Address1', 'Address2',
            'Address3', 'BankNumber', 'City', 'Country', 'DuplicateAction',
            'ExpirationDate', 'Priority', 'Protected', 'State', 'TelephoneNumber',
            'ZipCode',
        ],
        'function': put_create_paymentMethod,
    },
    # --- update payer ---
    'post_update_payer': {
        'required': ['PayerAccountId', 'Name'],
        'optional': ['EmailAddress', 'ExternalId1', 'ExternalId2'],
        'function': post_update_payer,
    },
    # --- authorize transaction ---
    'put_authorize_transaction': {
        'required': [
            'PayerAccountId', 'PaymentMethodID', 'Amount',
        ],
        'optional': ['IsRecurringPayment', 'CurrencyCode'],
        'function': put_authorize_transaction,
    },
    'put_capture_transaction': {
        'required': ['TransactionHistoryId', 'Amount'],
        'optional': [],
        'function': put_capture_transaction,
    },
    # --- void transaction ---
    'put_void_transaction': {
        'required': [],
        'optional': ['TransactionHistoryId', 'OriginalTransactionId'],
        'function': put_void_transaction,
    },
    # --- validate card ---
    # combination of put_authorize_transaction and put_void_transaction
    'put_validate_card': {
        'required': [
            'PayerAccountId', 'PaymentMethodID', 'Amount',
        ],
        'optional': [
            'IsRecurringPayment', 'CurrencyCode',
        ],
        'function': put_validate_card,
    },
    # --- update payment method ---
    'post_update_paymentMethod': {
        'required': [
            'PayerAccountId', 'PaymentMethodID', 'Protected', 'PaymentMethodType',
        ],
        'optional': [
            'AccountName', 'Address1', 'Address2', 'Address3', 'BankAccountType',
            'City', 'Country', 'Description', 'Email', 'ExpirationDate',
            'State', 'TelephoneNumber', 'ZipCode',
        ],
        'function': post_update_paymentMethod,
    },
    # --- delete payment method ---
    'delete_payMethod' : {
        'required': ['PayerAccountId', 'PaymentMethodID'],
        'optional': [],
        'function': delete_payMethod,
    },
    # --- delete payer ---
    'delete_PayerAccountId': {
        'required': ['PayerAccountId'],
        'optional': [],
        'function': delete_PayerAccountId,
    }
}

# ------------------------ helper function check_freqs ------------------------
def helper_check_freqs(rname, **kwargs) -> bool:
    """
    check for argument requirements in given request
    """

    required = FUNCTION_DICT[rname]['required']
    if len(required) > 0:
        rpass = True
        # --- check for function required arguments ---
        for key in required:
            if key not in kwargs:
                print(f"{key} missing")
                rpass = False
    else:
        # --- check that at least one optional requirement is present. ---
        rpass = False
        optional = FUNCTION_DICT[rname]['optional']
        for key in optional:
            if key in kwargs:
                rpass = True
                break

    return rpass


def api_http_request_controller(request, rname=None):
    """
    handle requests and sort by type, (GET/POST)

    - request keyword arguments are passed to their respective propay functions
    as a dictionary (rdict).  requests to propay using a URI query or JSON data
    do not require that all key:value pairs be valid, just that any required

    - make sure rname (request name) is valid
    - check for required arguments in request dict
    - call function if rname is valid, otherwise return with error info

    TODO:
        - [x] check for case where no required aruments but given optional
        - [ ] handle extra validations needed for POST requests

    """
    # --- return dict defaults to error, overwritten if api call works ---
    data = {}
    data['RequestResult'] = {'ResultValue': 'ERROR', 'ResultCode': '01'}

    # --- first check for valid rname ---
    if rname not in FUNCTION_DICT:
        data['message'] = f"rname {rname} not a valid API call"
        return data

    rfunction = FUNCTION_DICT[rname]['function']

    # --- extract data from request ---
    if request.method == "POST":
        rdict = request.POST.dict()
        # extra POST request validations here

    if request.method == "GET":
        rdict = request.GET.dict()

    # --- take any json and add to regular request data ---
    if 'json' in rdict:
        json_data = json.loads(rdict.pop('json'))
        rdict = {**rdict, **json_data}

    data = {**data, **rdict}

    # --- make sure requiredkeys is a string or list ---
    rpass = helper_check_freqs(rname, **rdict)

    if rpass:
        # --- call function with arglist, only takes named arguments as dictionary ---
        resp_propay = rfunction(**rdict)
        return resp_propay

    # --- error if not returned earlier ---
    return data


# -------------------------------------------------------------------------------
