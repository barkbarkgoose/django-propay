from django.test import TestCase, Client
from django.shortcuts import redirect
from django.urls import reverse
from pprint import pprint
from propay_api import config
from propay_api.propay import FUNCTION_DICT
from typing import Optional
from nested_lookup import nested_lookup
import requests
import json
import pdb

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
client = Client()

# --- send json data to request and print out what how that looks in a view ---
INIT_ACCT_DATA = {
    "Name": "Test Account",
    "EmailAddress":"email@email.com",    # email can't be looked up, just edited
    "ExternalId1":"12345",
    "ExternalId2":"Testaccount12",  # this will remain constant after payer update
}
INIT_CARD_DATA = {
    "PayerAccountId": "",  # update PayerAccountId value in tests
    "PaymentMethodType": "Visa",
    "AccountNumber": "4111111111111111",
    "ExpirationDate": "0823",
    "AccountCountryCode": "USA",
    "AccountName": "Janis Joplin",
    "BillingInformation": {
        "Address1": "123 ABC St",
        "Address2": "Apt. A",
        "Address3": "",
        "City": "Some Place",
        "Country": "USA",
        "Email": "",
        "State": "AK",
        "TelephoneNumber": "",
        "ZipCode": "12345",
    },
    "Description": "MyVisaCard",
    "Priority": "0",
    "DuplicateAction": "",
    "Protected": "false",
}

INIT_UPDATE_CARD = {
    "AccountName": "Updated Card",
    "ExpirationDate": "0824",
    "BillingInformation": {
        "Address1": "12345 ABC St",
        "Address2": "Apt. A",
        "City": "New Place",
        "Email": "email@email.com",
        "ZipCode": "12345",
    },
    "Protected": "false",
    "PaymentMethodType": "Visa",
}

INIT_VALIDATE_CARD = {
    "Amount": "100",
    # 'CreditCardOverrides': {
        'ExpirationDate': '1014',
        'CVV': '999',
    # },
}

INIT_UPDATE_PAYER = {
    'ExternalId1': '12333',
    'Name': 'Renamed Test',
    'EmailAddress': 'updatedemail@email.com',
}

ASSERT_PAYERDETAILS = {
    'ExternalId1': '12345',
    'ExternalId2': 'Testaccount12',
    'Name': 'Test Account',
    # "EmailAddress":"email@email.com",
}

ASSERT_UPDATE_PAYER = {
    'ExternalId1': '12333',
    'ExternalId2': 'Testaccount12',
    'Name': 'Renamed Test',
}

ASSERT_RESPONSE = {
    'ResultCode': '00',
    'ResultMessage': '',
    'ResultValue': 'SUCCESS',
}

ASSERT_PAYMETHOD = {
    "PaymentMethodType": "Visa",
    'ObfuscatedAccountNumber': '411111******1111',
    "ExpirationDate": "0823",
    "Country": "USA",
    "AccountName": "Janis Joplin",
    "Address1": "123 ABC St",
    "Address2": "Apt. A",
    "ZipCode": "12345"
}

ASSERT_UPDATE_PAYMETHOD = {
    "PaymentMethodType": "Visa",
    'ObfuscatedAccountNumber': '411111******1111',
    "ExpirationDate": "0824",
    "Country": "USA",
    "AccountName": 'Updated Card',
    "Address1": "12345 ABC St",
    "Address2": "Apt. A",
    "ZipCode": "12345",
    "City": "New Place",
    "Email": "email@email.com",
    "Protected": "False",
}

# ---------------- class to store persistent data between tests ----------------
class TestInstance:
    """
    Singleton TestInstance class
    creating an instance will alway reflect static class attributes
    ex:
        a = TestInstance()
        b = TestInstance()
        a == b              # True
        a == b == TestInstance   # True
    """
    _instance = None
    #
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TestInstance, cls).__new__(cls)
        #
        # return cls._instance
        return TestInstance
    #
    payerID_details = None
    paymethods = None
    assert_errors = []


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class PropayApiTest(TestCase):
    """
    helper functions to be used by other non-helper functions

    subtest functions not run when called by django test, but rather by another
    "test" function

    TODO:
    - [ ] send all print statements to logs with option to print to console
    """

    def helper_assert_return(self, rdata, assertlist) -> bool:
        """
        pprint everything in rdata
        takes a list of assertion dictionaries to compare with rdata

        TODO:
        - [x] expand asserts to make sure that more response data is correct
        """
        print("___data to be checked in assertions___")
        pprint(rdata)
        assert_pass = True
        error_reported = False
        # --- print out data response ---
        for subdict in assertlist:
            for key in subdict:
                val = nested_lookup(key, rdata)
                if len(val) == 0:
                    val = ''
                else:
                    val = val[0]
                    try:
                        self.assertEqual(str(subdict[key]), str(val))
                    except Exception as e:
                        if not error_reported:
                            TestInstance.assert_errors.append(
                                {
                                    "error": str(e),
                                    "rdata": rdata,
                                    "assertlist": assertlist,
                                }
                            )
                        else:
                            TestInstance.assert_errors.append(
                                {
                                    "error": str(e),
                                    "rdata": "^^^ see previous error",
                                }
                            )
                        error_reported = True
                        print("\n\n----------------------------------")
                        print(f"ERROR IN ASSERTION:\n{e}\n\n")

                # --- extra check for values, if any mismatch will return false
                if subdict[key] != val:
                    assert_pass = False

        return assert_pass


    def helper_make_request(self, rtype, uri, data) -> Optional[dict]:
        """
        make an http get or post request
        """
        if rtype == "GET":
            # response = self.client.get(reverse(uri), data=data)
            response = self.client.get(reverse(uri), data={'json':json.dumps(data)})
        else:
            response = self.client.post(reverse(uri), data={'json':json.dumps(data)})

        return response.json()


    def helper_set_testuri(self, **kwargs) -> dict:
        """
        sets testing values to be passed as optional kwargs to the api call functions
        - put into a single function so it's easy to turn off and on
        """
        kwargs = {
            **kwargs,
            'authoverride': (config.TEST_BILLER_ID, config.TEST_AUTH_TOKEN),
            'urioverride': config.TEST_PROTECTPAY_BASE_URI,
            'MerchantProfileId': config.TEST_MERCHANT_PROFILE_ID,
        }

        return kwargs


    def subtest_get_paymentMethod_details(self, **kwargs) -> dict:
        """
        Test to make request for card info for given payer.

        """
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "GET",
            uri='propayapi-paymethoddetails',
            data=kwargs
        )
        return rdata


    def subtest_put_create_payer(self, **kwargs) -> dict:
        """
        Test to create a new payer

        """
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-createpayer',
            data=kwargs
        )
        return rdata


    def subtest_put_validate_card(self, **kwargs) -> dict:
        """
        Test to validate card
            - authorizes $1 transaction
            - immediately voids transaction
        """
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-validatecard',
            data=kwargs
        )
        return rdata


    def subtest_get_payerID_details(self, **kwargs) -> dict:
        """
        Test to make sure that request can be made using INIT_ACCT_DATA to return
        info on a payer account.

        """
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "GET",
            uri='propayapi-payerdetails',
            data=kwargs
        )
        return rdata


    def subtest_put_create_paymentMethod(self, **kwargs) -> dict:
        """
        Test to create a new payment method (add a card)

        """
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-createpaymethod',
            data=kwargs
        )
        return rdata


    def subtest_update_payer(self, **kwargs) -> dict:
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-updatepayer',
            data=kwargs
        )
        return rdata


    def subtest_update_payMethod(self, **kwargs) -> dict:
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-updatepaymethod',
            data=kwargs
        )
        return rdata


    def subtest_delete_payMethod(self, **kwargs) -> dict:
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-deletepaymethod',
            data=kwargs
        )
        return rdata


    def subtest_delete_PayerAccountId(self, **kwargs) -> dict:
        kwargs = self.helper_set_testuri(**kwargs)
        rdata = self.helper_make_request(
            "POST",
            uri='propayapi-deletepayer',
            data=kwargs
        )
        return rdata

    # --------------------------------------------------------------------------
    def runtest_create_payer(self):
        print("\n\n--- PUT_CREATE_PAYER TEST ---")
        payerID_details = self.subtest_get_payerID_details(**INIT_ACCT_DATA)

        # --- if payer not already present create new ---
        if len(payerID_details['Payers']) == 0:
            self.subtest_put_create_payer(**INIT_ACCT_DATA)
            # --- update payerID_details ---
            payerID_details = self.subtest_get_payerID_details(**INIT_ACCT_DATA)

        # --- assert tests on data here ---
        TestInstance.payerID_details = payerID_details
        assertlist = [ASSERT_PAYERDETAILS, ASSERT_RESPONSE]
        rdata = TestInstance.payerID_details
        self.helper_assert_return(rdata, assertlist)


    # --------------------------------------------------------------------------
    def runtest_update_payer(self):
        print("\n\n--- UPDATE_PAYER TEST ---")
        # --- check that payer exists ---
        if TestInstance.payerID_details['Payers'] is None:
            return
        if len(TestInstance.payerID_details['Payers']) == 0:
            return

        # --- get payer and test request to update info ---
        payer = TestInstance.payerID_details['Payers'][0]
        payer_id = payer['payerAccountId']
        resp = self.subtest_update_payer(
            **{"PayerAccountId": payer_id, **INIT_UPDATE_PAYER},
        )
        assertlist = [ASSERT_RESPONSE]
        assert1 = self.helper_assert_return(resp, assertlist)

        # --- reload with updated payer info ---
        payerID_details = self.subtest_get_payerID_details(
            **{'ExternalId2': 'Testaccount12'},
            # **INIT_ACCT_DATA,
        )
        TestInstance.payerID_details = payerID_details

        # --- run assertions to check updated payer matches ---
        assertlist.append(ASSERT_UPDATE_PAYER)
        self.helper_assert_return(payerID_details, assertlist)

    # --------------------------------------------------------------------------
    def runtest_create_paymethod(self):
        print("\n\n--- PUT_CREATE_PAYMENTMETHOD TEST ---")
        # --- check that payer exists ---
        if TestInstance.payerID_details['Payers'] is None:
            return
        if len(TestInstance.payerID_details['Payers']) == 0:
            return

        # --- get first payer from list (should only be 1 normally) ---
        payer = TestInstance.payerID_details['Payers'][0]
        payerAccountId = payer['payerAccountId']
        INIT_CARD_DATA['PayerAccountId'] = payerAccountId

        # --- check for card info, add if not there ---
        TestInstance.paymethods = self.subtest_get_paymentMethod_details(
            **{'PayerAccountId': payerAccountId},
        )
        if len(TestInstance.paymethods['PaymentMethods']) == 0:
            self.subtest_put_create_paymentMethod(**INIT_CARD_DATA)
            TestInstance.paymethods = self.subtest_get_paymentMethod_details(
                **{'PayerAccountId': payerAccountId},
            )

        assertlist = [ASSERT_PAYMETHOD, ASSERT_RESPONSE]
        rdata = TestInstance.paymethods
        self.helper_assert_return(rdata, assertlist)

    # --------------------------------------------------------------------------
    def runtest_update_paymethod(self):
        print("\n\n--- UPDATE_PAYMETHOD TEST ---")
        if TestInstance.payerID_details['Payers'] is None:
            return
        if len(TestInstance.payerID_details['Payers']) == 0:
            return

        payer = TestInstance.payerID_details['Payers'][0]
        PayerAccountId = payer['payerAccountId']

        if TestInstance.paymethods is None:
            TestInstance.paymethods = self.subtest_get_paymentMethod_details(
                **{'PayerAccountId': PayerAccountId},
            )

        if len(TestInstance.paymethods['PaymentMethods']) > 0:
            card = TestInstance.paymethods['PaymentMethods'][0]
            PaymentMethodID = card['PaymentMethodID']
            rdata = self.subtest_update_payMethod(
                **{
                    'PayerAccountId': PayerAccountId,
                    'PaymentMethodID': PaymentMethodID,
                    **INIT_UPDATE_CARD,
                }
            )

            assertlist = [ASSERT_RESPONSE]
            assert1 = self.helper_assert_return(rdata, assertlist)
            # --- if update was successful run assertion on new card info ---
            if assert1 == True:
                TestInstance.paymethods = self.subtest_get_paymentMethod_details(
                    **{'PayerAccountId': PayerAccountId},
                )
                assertlist = [ASSERT_UPDATE_PAYMETHOD]
                card = TestInstance.paymethods['PaymentMethods'][0]
                self.helper_assert_return(card, assertlist)

    # --------------------------------------------------------------------------
    def runtest_validate_card(self):
        print("\n\n--- VALIDATE_CARD TEST ---")
        if TestInstance.payerID_details['Payers'] is None:
            return
        if len(TestInstance.payerID_details['Payers']) == 0:
            return

        payer = TestInstance.payerID_details['Payers'][0]
        PayerAccountId = payer['payerAccountId']

        if TestInstance.paymethods is None:
            TestInstance.paymethods = self.subtest_get_paymentMethod_details(
                **{'PayerAccountId': PayerAccountId},
            )

        if len(TestInstance.paymethods['PaymentMethods']) > 0:
            card = TestInstance.paymethods['PaymentMethods'][0]
            PaymentMethodID = card['PaymentMethodID']
            rdata = self.subtest_put_validate_card(
                **{
                    'PayerAccountId': PayerAccountId,
                    'PaymentMethodID': PaymentMethodID,
                    **INIT_VALIDATE_CARD,
                }
            )

        print(f"validation response: {rdata}")
        # run assertions here


    # --------------------------------------------------------------------------
    def runtest_delete_paymethod(self):
        print("\n\n--- DELETE_PAYMETHOD TEST ---")
        # --- check that payer exists ---
        if TestInstance.payerID_details['Payers'] is None:
            return
        if len(TestInstance.payerID_details['Payers']) == 0:
            return

        payer = TestInstance.payerID_details['Payers'][0]
        payerAccountId = payer['payerAccountId']

        if TestInstance.paymethods is None:
            TestInstance.paymethods = self.subtest_get_paymentMethod_details(
                **{'PayerAccountId': payerAccountId},
            )

        if len(TestInstance.paymethods['PaymentMethods']) > 0:
            # delete all paymethods here
            for card in TestInstance.paymethods['PaymentMethods']:
                PaymentMethodID = card['PaymentMethodID']
                rdata = self.subtest_delete_payMethod(
                    **{
                        'PayerAccountId': payerAccountId,
                        'PaymentMethodID': PaymentMethodID
                    }
                )
                assertlist = [ASSERT_RESPONSE]
                self.helper_assert_return(rdata, assertlist)

    # --------------------------------------------------------------------------
    def runtest_delete_PayerAccountId(self):
        """
        delete all payers
        """
        print("\n\n--- DELETE_PAYER TEST ---")
        # --- check that payer exists ---
        if TestInstance.payerID_details['Payers'] is None:
            return
        if len(TestInstance.payerID_details['Payers']) == 0:
            return

        payer_list = TestInstance.payerID_details['Payers']

        if not payer_list:
            # --- skip test if no payers ---
            print("no payers")
            return

        for payer in payer_list:
            payerAccountId = payer['payerAccountId']
            resp = self.subtest_delete_PayerAccountId(
                **{"PayerAccountId": payerAccountId}
            )
            self.helper_assert_return(resp, [ASSERT_RESPONSE])

    # --------------------------------------------------------------------------
    def test_all(self):
        """
        test all propay methods from start to finish, begin by searching for account
        using test info, then proceed to get card info, update ext ID2 then ID1,

        TESTING PROCESS:
            - check if payer already exists
                - if exists: delete
                - if not: create payer
            - add card
            - ?? charge card ??
                - void transaction
            - delete payer

        return all info on payer and card

        TODO:
        - [ ] implement "TESTING PROCESS"
            __payer tests__:
            - [x] create payer implemented in propay.py
            - [x] avoid adding duplicate? (check for error in trying)
                - [x] api call doesn't check, but test does
            - [x] update payer details
                - [x] externalId1
                - [x] externalId2
                - [x] name
                - [x] email   ### can update but current lookup doesn't show email
            - [x] add card implemented in propay.py
            - [x] view card details
            - [x] update card
            - [x] delete card
            - [ ] validate card
                - [x] authorize transaction
                - [ ] void transaction
            - [ ] authorize then capture transaction  **(not needed?)
            - [ ] process transaction (skip authorization)
            - [ ] credit payment method


            __independent tests__:
            ?? Q's:
                is there a way to process a hosted transaction and look up an existing
                account in the process?
                    - have them enter an account number, if it matches hosted_transaction
                    will add new card to that.  run as "external_add_card" view/function

            - [ ] hosted transaction
                - [ ] create payer (if not already present)
                - [ ] process transaction

            - [ ] process one time transaction     # see docs section 7.1
                - [ ] add a recurring transaction
            - [ ] void transaction

        - [ ] separate test class for each type of api call (payer, transaction, method)
        - [ ] check against expected values, not just response code

        """
        # --- create/update tests ---
        self.runtest_create_payer()
        self.runtest_update_payer()
        self.runtest_create_paymethod()
        self.runtest_update_paymethod()

        # --- card validation test ---
        self.runtest_validate_card()

        # --- transaction tests ---


        # --- deletion tests ---
        self.runtest_delete_paymethod()
        self.runtest_delete_PayerAccountId()

        # --- pause if errors found in assertions ---
        print(f"\n\n---------------------- ERROR REPORT ----------------------")
        if len(TestInstance.assert_errors) > 0:
            print("\n\n----------------------------------------")
            print("errors found in tests...")
            print("\nerror list:")
            print(f"{pprint(TestInstance.assert_errors)}")

        print(f"\nTOTAL ASSERTION ERRORS: {len(TestInstance.assert_errors)}")

    # --------------------------------------------------------------------------
