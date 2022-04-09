from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse

from propay_ui.models import Payer

import pdb
"""
decorators meant to be paired with views and controller functions

NOTE: should not use any project or app-level modules (except models.py) to avoid
circular imports
"""

# ----------------------- GET USER CACHE, REQUIRE PAYER ------------------------
def get_usercache_require_payer(view_func):
    """
    try to get payer from usercache or request data.
    - add lookval to usercache

    payer object found?:
        NO --> redirect to payersearch page
        YES --> add usercache to kwargs
    """
    def wrapper(request, **kwargs):
        uid = request.user.id
        cachename = f"propayui-{uid}"
        usercache = cache.get_or_set(cachename, {}, timeout=60*60*24)

        # --- set up lookval in usercache ---
        if 'lookval' in usercache:
            pass
        else:
            usercache['lookval'] = None

        # --- check for payer in usercache ---
        if 'payer' in usercache:
            cache.touch(cachename, timeout=60*60*24)

        else:
            # --- see if payer can be initialized from request info ---
            payer = Payer.init_from_request(request)
            if payer:
                usercache['payer'] = payer
                cache.set(cachename, usercache, timeout=60*60*24)
            else:
                # --- payer not in cache, redirect to search page ---
                return redirect('propayui-payersearch')

        # --- call view function here ---
        kwargs['usercache'] = usercache
        return view_func(request, **kwargs)

    return wrapper

# -------------------------- GET USER CACHE - LOOKVAL --------------------------
def log_viewaccess(view_func):
    def wrapper(request, **kwargs):
        uid = request.user.id
        # uname = request.user.name
        view_resp = view_func(request, **kwargs)
        return view_resp
    return wrapper


# ------------------------------------------------------------------------------
