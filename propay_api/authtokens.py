BILLER_ID = '8299147762710652'
AUTH_TOKEN = '339a8782-8d8f-490c-9ae8-ce9efa3d4bd3'
MERCHANT_PROFILE_ID = '715854982'
TEST_PIN = '65306'
# vespa: 192.168.1.31

# --- TESTING AUTHENTICATION ---
"""
    - BillerId
    - AuthorizationToken
    - MerchantProfileId
    I got these by emailing clientsupport@propay.com and requesting for the
    integration URI https://xmltestapi.propay.com/ProtectPay/
"""
TEST_BILLER_ID = '2766248617288673'
TEST_AUTH_TOKEN = '1d743535-310f-4feb-9900-d63fa9b71b7f'
TEST_MERCHANT_PROFILE_ID = '2849249'

# --- things for testing ---
import base64
TEST_ACCOUNT = '718212729'
TEST_PASSWORD = 'yZ5n@%yQkB'
TEST_EMAIL = 'jake@faxpipe.com'
testuri = 'https://xmltestapi.propay.com/propayapi/signup'
myCertStr = 'dfweqwqesder737237awei23ew7u33'
myTermId = 'bleh'
# --- 1: combine CertStr, a Colon, and the termId ---
cert = f'{myCertStr}:{myTermId}'
# --- 2: Convert Result of step 1 to an ASCII Byte array ---
barr = bytearray(cert.encode('ascii'))
# --- 3: Base 64 encode the result of step 2 ---
cert64 = base64.b64encode(barr)
# --- 4: prepend "Basic" to the result of step 3 ---
# certfinal used to authenticate test uri calls with an "Authentication" header
# in the request.
certfinal = b'Basic ' + cert64
# --- vvv the result vvv ---
# --- bytes aren't json serializable so just save as string and let the api calls
# handle the rest ---
TEST_AUTH = 'Basic ZGZ3ZXF3cWVzZGVyNzM3MjM3YXdlaTIzZXc3dTMzOmJsZWg='
