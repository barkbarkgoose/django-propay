from django.urls import path, re_path
from propay_ui import views

# ---------------------------------- patterns ----------------------------------
urlpatterns = [
    re_path(
        r'^$',
        views.index,
        name="propayui-index",
    ),
    re_path(
        r'^cardadd/?$',
        views.card_add,
        name="propayui-cardadd",
    ),
    re_path(
        r'^carddelete/(?P<cardid>.+)?/?$',
        views.card_delete,
        name="propayui-carddelete",
    ),
    re_path(
        r'^cardedit/(?P<cardid>.+)?/?$',
        views.card_edit,
        name="propayui-cardedit",
    ),
    re_path(
        r'^cardverify/(?P<cardid>.+)?/?$',
        views.card_verify,
        name="propayui-cardverify",
    ),
    re_path(
        r'^payercreate/?$',
        views.payer_create,
        name="propayui-payercreate",
    ),
    re_path(
        r'^payerdelete/(?P<lookval>.+)?/?$',
        views.payer_delete,
        name="propayui-payerdelete",
    ),
    re_path(
        r'^payerdetails/(?P<lookval>.+)?/?$',
        views.payer_details,
        name="propayui-payerdetails",
    ),
    re_path(
        # lookval and payer object in cache
        r'^payerdetails/?$',
        views.payer_details,
        name="propayui-payerdetails",
    ),
    re_path(
        r'^payersearch/(?P<lookval>.+)?/?$',
        views.payer_search,
        name="propayui-payersearch",
    ),
    re_path(
        # lookval in cache
        r'^payersearch/?$',
        views.payer_search,
        name="propayui-payersearch",
    ),
    re_path(
        r'^payerupdate/(?P<lookval>.+)?/?$',
        views.payer_update,
        name="propayui-payerupdate",
    ),
    re_path(
        r'^transsearch/?$',
        views.trans_search,
        name="propayui-transsearch",
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
