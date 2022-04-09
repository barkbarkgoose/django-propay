import os

# ---- Build paths inside the project like this: os.path.join(BASE_DIR, ...) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------- PROPAY -----------------------------------
PROTECTPAY_BASE_URI = 'https://api.propay.com/ProtectPay/'
PROTECTPAY_PAYER_API = 'https://api.propay.com/ProtectPay/Payers/'
PROTECTPAY_TRANSACTION_API = 'https://api.propay.com/ProtectPay/HostedTransactions/'
PROTECTPAY_TRANSACTION_INFO = 'https://api.propay.com/protectpay/HostedTransactionResults/'
PROTECTPAY_PAYMENT_URL = 'https://protectpay.propay.com/hpp/v2/'
PROTECTPAY_VOID_API = 'https://api.propay.com/protectpay/VoidedTransactions/'


# ------------------------------------ AUTH ------------------------------------
# auth tokens kept separate in non tracked file `authtokens`
from propay_api.authtokens import BILLER_ID
from propay_api.authtokens import AUTH_TOKEN
from propay_api.authtokens import MERCHANT_PROFILE_ID
from propay_api.authtokens import TEST_PIN
from propay_api.authtokens import TEST_ACCOUNT
from propay_api.authtokens import TEST_PASSWORD
from propay_api.authtokens import TEST_BILLER_ID
from propay_api.authtokens import TEST_AUTH_TOKEN
from propay_api.authtokens import TEST_MERCHANT_PROFILE_ID

# -------------- css and custom and return urls can be customized --------------
CSS_URL = 'https://protectpaytest.propay.com/hpp/css/pmi.css'
# CSS_URL = 'https://propay.com/hpp/css/pmi.css'
RETURN_URL = 'returnfromcc/'


#  ------------------------------- PROPAY TESTS --------------------------------
TEST_PROTECTPAY_BASE_URI = 'https://xmltestapi.propay.com/ProtectPay/'
TEST_PROTECTPAY_PAYER_API = 'https://xmltestapi.propay.com/ProtectPay/Payers/'
TEST_PROTECTPAY_TRANSACTION_API = 'https://xmltestapi.propay.com/ProtectPay/HostedTransactions/'
TEST_PROTECTPAY_TRANSACTION_INFO = 'https://xmltestapi.propay.com/ProtectPay/HostedTransactionResults/'
TEST_PROTECTPAY_PAYMENT_URL = 'https://xmltestapi.propay.com/ProtectPay/hpp/v2/'
TEST_PROTECTPAY_VOID_API = 'https://xmltestapi.propay.com/ProtectPay/VoidedTransactions/'
# TEST_PROTECTPAY_PAYMENT_URL = 'https://protectpaytest.propay.com/hpp/v2/'

# --- old junk stuff ---
# TEST_BILLER_ID = '7310599495234916'
# TEST_AUTH_TOKEN = '2a44f9bd-d3c6-40e0-8988-7c1853e13396'
#
# TEST_BILLER_ID2 = '9999986379225246'
# TEST_AUTH_TOKEN2 = '16dfe8d7-889b-4380-925f-9c2c6ea4d930'
