from django.shortcuts import render
from propay_api.config import BILLER_ID, AUTH_TOKEN, MERCHANT_PROFILE_ID
from propay_api.config import CSS_URL

# Create your views here.
def create_hosted_transaction(request, **kwargs):
    """
    - if no linked payerAccountId create new payer
    - create hosted transaction instance for payer
    -
    """


    transaction_data = {
        # "BillerAccountID" => env('BILLER_ID'),
        # "AuthorizationToken" : env('AUTH_TOKEN'),
        "PayerAccountId" : "payerAccountId",
        # "MerchantProfileId" : '2305383',
        "MerchantProfileId" : MERCHANT_PROFILE_ID, # ? faxpipe profile id ?
        "Amount" : plan['propay'],
        "CurrencyCode" : "USD",
        "InvoiceNumber" : "Account Signup",
        # "InvoiceNumber" : $decoded['HostedTransactionIdentifier'];
        "Comment1" : plan['description'],
        "CardHolderNameRequirementType" : 1,
        "SecurityCodeRequirementType" : 1,
        "AvsRequirementType" : 1,
        # "AuthOnly" : False,
        # "ProcessCard" : True,
        "StoreCard" : True,
        "OnlyStoreCardOnSuccessfulProcess" : False,
        "CssUrl" : CSS_URL,
        "BillerIdentityId" : None,
        "CreationDate" : None,
        "HostedTransactionIdentifier" : None,
        "PaymentTypeId" : "0",   # 0: card, 1: ACH
        "Protected" : False,
        # --- things filled in by form ---
        "ReturnURL" : return_url,
        "Address1" : account.address,
        "Address2" : '',
        "City" : account.city,
        "Country" : 'USA',
        "Description" : '',
        "Name" : account.first_name + ' ' + account.last_name,
        "State" : account.state,
        "ZipCode" : account.zip,
    }

    # --- PLAN SPECIFIC ---
    AuthOnly = None
    ProcessCard = None
    InvoiceNumber = None
    OnlyStoreCardOnSuccessfulProcess = None

    pass
