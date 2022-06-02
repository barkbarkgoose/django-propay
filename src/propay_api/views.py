import json
import pdb
# import propay_api
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.response import TemplateResponse

# --- project imports ---
from . import propay

"""
TODO:
- [ ] move index view to propay-ui app
    - [ ] propay-api should not accept empty urls
    - [ ] 404 error shoudl return JSON response saying not a valid URI
"""

# ------------------------------ helper functions ------------------------------

# ******************************************************************************
# *** API CALLS
# ******************************************************************************
"""
SAMPLE_DATA = {
    "Name": "Test Account",
    "EmailAddress":"test@test.tst",
    "ExternalId1":"12345",
    "ExternalId2":"Testaccount12",
}
"""
# # --------------------------- AUTHORIZE TRANSACTION ----------------------------
# def put_authorize_transaction(request):
#     pass
#
#
# # ---------------------------- CAPTURE TRANSACTION -----------------------------
# def put_capture_transaction(request):
#     pass
#
#
# -------------------------------- PROPAY API ----------------------------------
def hosted_transaction(request):
    pass


# ---------------------------- GET TRANSACTION DATA ----------------------------
def get_transaction_info(request) -> JsonResponse:
    pass


# ------------------------------ VOID TRANSACTION ------------------------------
def put_void_transaction(request) -> JsonResponse:
    result = propay.api_http_request_controller(
        request,
        rname='put_void_transaction',
    )

    return JsonResponse(result)


# ------------------------------- VALIDATE CARD --------------------------------
def put_validate_card(request) -> JsonResponse:
    result = propay.api_http_request_controller(
        request,
        rname='put_validate_card',
    )

    return JsonResponse(result)


# -------------------------------- CREATE PAYER --------------------------------
def put_create_payer(request) -> JsonResponse:
    """
    EXAMPLE INTERNAL REQUEST:
        propay.put_create_payer(SAMPLE_DATA)

    EXAMPLE EXTERNAL REQUEST:
        resp = requests.put(
            'http://your.hostname.com/propay/createpayer',
            SAMPLE_DATA,
        )
    """
    result = propay.api_http_request_controller(
        request,
        rname='put_create_payer',
    )

    return JsonResponse(result)


# -------------------------------- UPDATE PAYER --------------------------------
def post_update_payer(request) -> JsonResponse:
    """
    EXAMPLE INTERNAL REQUEST:
        propay.post_update_payer(SAMPLE_DATA)

    EXAMPLE EXTERNAL REQUEST:
        resp = requests.post(
            'http://your.hostname.com/propay/updatepayer',
            SAMPLE_DATA,
        )
    """
    result = propay.api_http_request_controller(
        request,
        rname='post_update_payer',
    )

    return JsonResponse(result)


# --------------------------- CREATE PAYMENT METHOD ----------------------------
def put_create_paymentMethod(request) -> JsonResponse:
    """
    **see TEST_CARD_DATA in tests.py

    EXAMPLE INTERNAL REQUEST:
        propay.put_create_paymentMethod(TEST_CARD_DATA)

    EXAMPLE EXTERNAL REQUEST:
        resp = requests.put(
            'http://your.hostname.com/propay/createpaymethod',
            TEST_CARD_DATA,
        )
    """
    result = propay.api_http_request_controller(
        request,
        rname='put_create_paymentMethod',
    )

    return JsonResponse(result)


# --------------------------- UPDATE PAYMENT METHOD ----------------------------
def post_update_paymentMethod(request) -> JsonResponse:
    result = propay.api_http_request_controller(
        request,
        rname='post_update_paymentMethod',
    )

    return JsonResponse(result)


# --------------------------- DELETE PAYMENT METHOD ----------------------------
def post_delete_paymentMethod(request) -> JsonResponse:
    """

    """
    result = propay.api_http_request_controller(
        request,
        rname='delete_payMethod',
    )

    return JsonResponse(result)


# ------------------------------- DELETE PAYER ---------------------------------
def post_delete_PayerAccountId(request) -> JsonResponse:
    """

    """
    result = propay.api_http_request_controller(
        request,
        rname='delete_PayerAccountId',
    )

    return JsonResponse(result)


# ------------------------------- GET PAYER INFO -------------------------------
def get_payerID_details(request) -> JsonResponse:
    """
    SAMPLE_DATA = {'Identifier': '#####'}

    EXAMPLE INTERNAL REQUEST:
        propay.get_payerId_details('#####')

    EXAMPLE EXTERNAL REQUEST:
        resp = requests.get(
            'http://your.hostname.com/propay/payerdetails',
            SAMPLE_DATA,
        )
    """
    result = propay.api_http_request_controller(
        request,
        rname='get_payerId_details',
    )

    return JsonResponse(result)



# ------------------------- GET PAYMENT METHOD DETIALS -------------------------
def get_paymentMethod_details(request) -> JsonResponse:
    """
    SAMPLE_DATA = {'payerID': '################'}

    EXAMPLE INTERNAL REQUEST:
        propay.get_paymentMethod_details(SAMPLE_DATA)

    EXAMPLE EXTERNAL REQUEST:
        resp = requests.get(
            'http://your.hostname.com/propay/payerdetails',
            SAMPLE_DATA,
        )
    """
    result = propay.api_http_request_controller(
        request,
        rname='get_paymentMethod_details',
    )

    return JsonResponse(result)
