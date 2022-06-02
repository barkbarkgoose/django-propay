from django.urls import path, re_path
from propay_api import views

# ---------------------------------- patterns ----------------------------------
urlpatterns = [
    re_path(
        r'payerdetails/?$',
        views.get_payerID_details,
        name="propayapi-payerdetails"
    ),
    re_path(
        r'paymethoddetails/?$',
        views.get_paymentMethod_details,
        name="propayapi-paymethoddetails"
    ),
    # re_path(
    #     r'authorizetransaction/?$',
    #     views.put_authorize_transaction,
    #     name="propayapi-authorizetransaction"
    # ),
    # re_path(
    #     r'capturetransaction/?$',
    #     views.put_capture_transaction,
    #     name="propayapi-capturetransaction"
    # ),
    re_path(
        r'validatecard/?$',
        views.put_validate_card,
        name="propayapi-validatecard"
    ),
    re_path(
        r'voidtransaction/?$',
        views.put_void_transaction,
        name="propayapi-voidtransaction"
    ),
    re_path(
        r'createpayer/?$',
        views.put_create_payer,
        name="propayapi-createpayer"
    ),
    re_path(
        r'createpaymethod/?$',
        views.put_create_paymentMethod,
        name="propayapi-createpaymethod"
    ),
    re_path(
        r'deletepaymethod/?$',
        views.post_delete_paymentMethod,
        name="propayapi-deletepaymethod"
    ),
    re_path(
        r'deletepayer/?$',
        views.post_delete_PayerAccountId,
        name="propayapi-deletepayer"
    ),
    re_path(
        r'updatepayer/?$',
        views.post_update_payer,
        name="propayapi-updatepayer"
    ),
    re_path(
        r'updatepaymethod/?$',
        views.post_update_paymentMethod,
        name="propayapi-updatepaymethod"
    ),
]

# ------------- litss of request types to be automatically tested --------------
# test_post_list = [
#     'propayapi-tests',
# ]
#
# test_get_list = [
#
# ]
