from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from json2html import json2html
from propay_api import propay
from propay_ui import controller
from propay_ui.forms import CardAddForm, CardEditForm, LookupForm, PayerCreateForm
from propay_ui.forms import PayerUpdateForm, TransactionLookupForm
from propay_ui.models import Payer
from propay_ui.view_decorators import get_usercache_require_payer, log_viewaccess
# from propay_ui.view_decorators import get_usercache_lookval

import json
import pdb

# --- initialize cache for this app ---
### (add_key only changes value if key isn't already present)
# cache.add_key('propay_ui', {}, timeout=None)
# propay_ui_cache = cache.get('propay_ui')

# --------------------------------- INDEX VIEW ---------------------------------
@login_required
# @log_viewaccess
def index(request):
    # --- clear cache for user ---
    controller.clear_usercache(request.user.id)

    return render(request, "propay_ui/index.html")

# ---------------------------------- CARD ADD ----------------------------------
@login_required
@get_usercache_require_payer
def card_add(request, **kwargs):
    # --- function level variables ---
    usercache = kwargs['usercache']
    payer = usercache['payer']
    cardresp = propay.get_paymentMethod_details(PayerAccountId=payer.pid)
    cardlist = cardresp['PaymentMethods']

    # --- initialize form ---
    if request.method == "GET":
        form = CardAddForm(
            initial={
                "PayerAccountId": payer.pid,
                "DuplicateAction": 'Error',
            }
        )

    # --- handle form submission ---
    if request.method == "POST" and len(cardlist) < 9:
        form = CardAddForm(request.POST)
        if form.is_valid():
            reqdata = form.cleaned_data
            # --- send request to api ---
            controller.log_user_access(request.user, 'card_add')
            resp = propay.put_create_paymentMethod(**reqdata)

            if resp and resp['RequestResult']['ResultValue'] == 'SUCCESS':
                # --- api call successful ---
                return redirect('propayui-payerdetails')
            else:
                # --- api call failed ---
                if resp['RequestResult']['ResultMessage'] == "propayDetail is null":
                    message = "unknown error returned from propay. "
                    message += "check for duplicate card before trying again"
                    resp['RequestResult']['ResultMessage'] = message

                message = resp

    # --- make sure no more than 9 cards are exceeded ---
    if len(cardlist) > 8:
        form = None
        message = {
            'RequestResult':{
                "Status": "Error",
                "Message": """Card limit is 9 per payer.
                    Delete a card before adding another."""
            }
        }

    if 'message' not in locals(): message = None
    context = {"form": form, "payer": payer, "message": message}

    return render(request, "propay_ui/card_add.html", context)

# -------------------------------- CARD DELETE ---------------------------------
@login_required
@get_usercache_require_payer
def card_delete(request, **kwargs):
    """
    page to confirm card deletion
    """
    card = None
    message = None
    usercache = kwargs['usercache']
    payer = usercache['payer']
    cardid = kwargs['cardid']

    if request.method == "GET":
        cardresp = propay.get_paymentMethod_details(PayerAccountId=payer.pid)
        cardlist = cardresp['PaymentMethods']

        for item in cardlist:
            if item['PaymentMethodID'] == cardid:
                card = item
                break

    if request.method == "POST":
        controller.log_user_access(request.user, 'delete_payMethod')
        message = propay.delete_payMethod(
            PayerAccountId=payer.pid,
            PaymentMethodID=cardid,
        )

    context = {'card': card, 'message': message}

    return render(request, 'propay_ui/card_delete.html', context)

# --------------------------------- CARD EDIT ----------------------------------
@login_required
@get_usercache_require_payer
def card_edit(request, **kwargs):
    """
    edit payer card info
    NOTE:
        propay returns PaymentMethodID with "ID" being capitalized, but in requests
        they require that to be PaymentMethodId ("Id"). Our api handler anticipates
        the format propay returns, so as such both cases are added to the call
        between our UI and API handler... just in case.
    """
    card = None
    message = None
    usercache = kwargs['usercache']
    payer = usercache['payer']
    cardid = kwargs['cardid']

    if request.method == "GET":
        # --- get card info ---
        cardresp = propay.get_paymentMethod_details(PayerAccountId=payer.pid)
        cardlist = cardresp['PaymentMethods']

        for item in cardlist:
            if item['PaymentMethodID'] == cardid:
                card = item
                card['PaymentMethodId'] = card['PaymentMethodID']
                break

        ### separate billing sub-dict from card dict
        bill_info = card.pop("BillingInformation")

        # --- initialize form ---
        form = CardEditForm(
            initial={
                "PayerAccountId": payer.pid,
                **card,
                **bill_info,
            }
        )

    # --- handle form submission ---
    if request.method == "POST":
        form = CardEditForm(request.POST)
        if form.is_valid():
            reqdata = form.cleaned_data
            reqdata['PaymentMethodID'] = reqdata['PaymentMethodId']
            # --- send request to api ---
            controller.log_user_access(request.user, 'post_update_paymentMethod')
            resp = propay.post_update_paymentMethod(**reqdata)

            if resp and resp['ResultValue'] == 'SUCCESS':
                # --- api call successful ---
                return redirect('propayui-payerdetails')
            else:
                # --- api call failed ---
                message = resp

    if 'message' not in locals(): message = None
    context = {"form": form, "payer": payer, "message": message, 'cardid': cardid}

    return render(request, "propay_ui/card_add.html", context)

# -------------------------------- CARD VERIFY ---------------------------------
@login_required
@get_usercache_require_payer
def card_verify(request, **kwargs):
    """
    Authorize a transaction and immediately void if successful.  Successfully
    completing the first step signifies that the card is valid.  Voiding an authorized
    transaction ensures that those funds are not
    """
    card = None
    message = None
    usercache = kwargs['usercache']
    payer = usercache['payer']
    cardid = kwargs['cardid']

    # if request.method == "GET":

    cardresp = propay.get_paymentMethod_details(PayerAccountId=payer.pid)
    cardlist = cardresp['PaymentMethods']

    for item in cardlist:
        if item['PaymentMethodID'] == cardid:
            card = item
            break

    controller.log_user_access(request.user, 'card_verify')
    message = propay.put_validate_card(
        PayerAccountId=payer.pid,
        PaymentMethodID=cardid,
    )

    context = {'card': card, 'message': message}

    return render(request, 'propay_ui/card_validate.html', context)

# -------------------------------- PAYER DETAILS -------------------------------
@login_required
@get_usercache_require_payer
def payer_details(request, **kwargs):
    """
    @request: []
    @kwargs: []
    # GET --> view
    # POST -->
    # logic process:
        - add lookval and payer to cache
        - get card list for payer
    """
    # --- function level variables ---
    uid = request.user.id
    usercache = kwargs['usercache']
    payer = usercache['payer']

    # --- lookval in kwargs when sent from search page, add to userache ---
    if 'lookval' in kwargs:
        usercache['lookval'] = kwargs['lookval']
        controller.update_usercache(uid, usercache)

    cardresp = propay.get_paymentMethod_details(PayerAccountId=payer.pid)
    cardlist = cardresp['PaymentMethods']

    context = {
        'payer': payer,
        'cardlist': cardlist,
    }

    return render(request, 'propay_ui/payer_details.html', context)

# -------------------------------- PAYER CREATE --------------------------------
@login_required
def payer_create(request, **kwargs):
    """
    - POST makes API call
    - GET goes to view
    """
    # --- function-level variables ---
    data = None
    uid = request.user.id

    # --- ensure cache is clear (also done after successful payer creation)---
    controller.clear_usercache(uid)

    if request.method == "GET":
        form = PayerCreateForm()

    else:
        form = PayerCreateForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data

            # --- check for duplicate payer with with same ExternalId1 ---
            r0 = propay.get_payerId_details(**{"ExternalId1": data['ExternalId1']})['Payers']
            if len(r0) == 0:
                # --- submit data to ProtectPay to create payer ---
                controller.log_user_access(request.user, 'put_create_payer')
                resp = propay.put_create_payer(**data)

                if "ExternalAccountID" in resp:
                    # --- take data returned from ProtectPay and get payer object ---
                    payer = Payer(
                        resp['ExternalAccountID'],
                        data["Name"],
                        data["ExternalId1"],
                        data["ExternalId2"],
                    )
                    # --- overwrite usercache with payer, set lookval as eid1 ---
                    usercache = {
                        'lookval': payer.name,
                        'payer': payer,
                    }
                    controller.update_usercache(uid, usercache)

                    # --- redirect to payer details page ---
                    return redirect(reverse('propayui-payerdetails'))

                else:
                    # --- error response from ProtectPay ---
                    data = resp

            else:
                errmsg = "Another user is already linked to same account number"
                form.add_error("ExternalId1", errmsg)
                data = errmsg

        else:
            # --- erorr in form submission ---
            data = "form invalid"


    context = {'form': form, 'data': data}

    return render(request, 'propay_ui/payer_create.html', context)

# -------------------------------- PAYER DELETE --------------------------------
@login_required
@get_usercache_require_payer
def payer_delete(request, **kwargs):
    """
    @request.POST: [payerid]
    @kwargs: []
    # GET --> view
    # POST --> propay.delete_PayerAccountId
    # logic process:
        - get/set lookval using cache
        - if POST request attempt to delete payer
            - return to page with message about deletion attempt
    """
    # --- function level variables ---
    uid = request.user.id
    usercache = kwargs['usercache']
    lookval = usercache['lookval']
    payer = usercache['payer']

    if request.method == "POST" and 'payerid' in request.POST:
        # --- make request to delete payer from ProtectPay ---
        payerid = request.POST['payerid']
        if payerid != "" and payerid == payer.pid:
            controller.log_user_access(request.user, 'delete_PayerAccountId')
            resp = propay.delete_PayerAccountId(PayerAccountId=payerid)
            if resp and resp['ResultValue'] == 'SUCCESS':
                # --- remove payer from cache ---
                usercache = {'lookval': lookval}
                controller.update_usercache(uid, usercache)
                deleted = True
                message = "Payer Deleted Successfully"
            else:
                message = f"PAYER NOT DELETED. \nPropay response: {resp}"
        else:
            message = "Error payer ID not present"

        # --- add result message to context ---
        context = {'message': message}

    else:
        context = {'payer': payer}

    return render(request, "propay_ui/payer_delete.html", context)

# ----------------------------- PAYER SEARCH VIEW ------------------------------
@login_required
def payer_search(request, **kwargs):
    # --- function level variables ---
    form = LookupForm(request.GET or None)
    uid = request.user.id
    usercache = controller.get_or_set_usercache(uid)
    context = {}
    payerlist = []

    # --- get lookval from cache/kwargs, update cache ---
    lookval = controller.get_cached_lookval(usercache, kwargs)

    # --- get lookval from form submission ---
    if request.method == "GET":
        if form.is_valid():
            # --- search ProtectPay API with submitted value ---
            data = form.cleaned_data
            lookval = data.get("lookval")

    # --- connect to api and run search ---
    if lookval and len(lookval) > 0:
        # --- search for extid1, extid2, then name... return combined ---
        r0 = propay.get_payerId_details(**{"ExternalId1": lookval})['Payers']
        r1 = propay.get_payerId_details(**{"ExternalId2": lookval})['Payers']
        r2 = propay.get_payerId_details(**{"Name": lookval})['Payers']

        pid_list = []
        for rlist in [r0, r1, r2]:
            for pdict in rlist:
                pid = pdict['payerAccountId']
                # --- only add each pid once ---
                if pid not in pid_list:
                    name = pdict['Name']
                    eid1 = pdict['ExternalId1']
                    eid2 = pdict['ExternalId2']
                    payer = Payer(pid, name, eid1, eid2)
                    pid_list.append(pid)
                    payerlist.append(payer)

    # --- set/update cache with new lookval value (this wipes the payer as well) ---
    controller.update_usercache(uid, {'lookval': lookval})

    context["form"] = form
    context['search_results'] = payerlist

    return render(request, "propay_ui/payer_search.html", context)

# -------------------------------- PAYER UPDATE --------------------------------
@login_required
@get_usercache_require_payer
def payer_update(request, **kwargs):
    """

    """
    # --- function level variables ---
    uid = request.user.id
    usercache = kwargs['usercache']
    payer = usercache['payer']
    data = ""

    if request.method == "GET":
        form = PayerUpdateForm(
            initial = {
                'Name': payer.name,
                'ExternalId1': payer.eid1,
                'ExternalId2': payer.eid2,
            }
        )

    else:
        form = PayerUpdateForm(request.POST or None)
        if form.is_valid():
            data = form.data
            payer.name = data.get('Name')
            payer.eid1 = data.get('ExternalId1')
            payer.eid2 = data.get('ExternalId2')

            rdata = {
                "PayerAccountId": payer.pid,
                "Name": payer.name,
                "ExternalId1": payer.eid1,
                "ExternalId2": payer.eid2,
            }
            # --- check if another payerid already has the same ExternalId1 ---
            r0 = propay.get_payerId_details(**{"ExternalId1": payer.eid1})['Payers']
            if len(r0) == 0:
                controller.log_user_access(request.user, 'post_update_payer')
                resp = propay.post_update_payer(**rdata)
                data = resp

                if resp and resp['ResultValue'] == 'SUCCESS':
                    # --- change made successfully. update payer in usercache ---
                    usercache['payer'] = payer
                    controller.update_usercache(uid, usercache)
            else:
                errmsg = "Another user is already linked to same account number"
                form.add_error("ExternalId1", errmsg)
                data = errmsg

    context = {
        'payer': payer,
        'form': form,
        'data': data,
    }

    return render(request, "propay_ui/payer_update.html", context)

# --------------------------------- TRANS VOID ---------------------------------
@login_required
def trans_search(request):
    """
    transaction search page.
    get requests with a form submission will attempt a lookup through the api.
    """
    # --- function level variables ---
    form = TransactionLookupForm(request.GET or None)
    lookval = None
    search_results = None
    message = None

    # --- get lookval from form submission ---
    if request.method == "GET":
        if form.is_valid():
            # --- search ProtectPay API with submitted value ---
            data = form.cleaned_data
            lookval = data.get("lookval")

    # --- search for transaction ID ---
    if lookval and len(lookval) > 0:
        resp = propay.get_transaction_info(HostedTransactionId=lookval)

        if resp['Result']['ResultValue'] == "SUCCESS":
            search_results = resp['HostedTransaction']

        if not search_results:
            message = "Transaction Not Found"


    context = {
        'form': form,
        'search_results': search_results,
        'message': message,
    }

    return render(request, "propay_ui/trans_search.html", context)

# ------------------------------------------------------------------------------
