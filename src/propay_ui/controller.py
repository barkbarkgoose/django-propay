from typing import Optional, Union
from django.core.cache import cache
import logging
# ------------------------ PAYER DETAILS CACHE HANDLING ------------------------
# def retr_cached_payer(cache) -> Union[object, None]:
#     cachekeys = cache.keys("*")
#     if 'payer' in cachekeys:
#         payer = cache.get('payer')
#         return payer
#     else:
#         return None
infologger = logging.getLogger("propay")
debuglogger = logging.getLogger("propay.debug")

# ------------------------------ LOG USER ACCESS -------------------------------
def log_user_access(user, fname):
    """
    log the user and intended api call
    """
    message = f"user: {user.id}|{user.username} - call: {fname}"
    infologger.info(message)

# ---------------------- GET LOOKVAL FROM CACHE OR KWARGS ----------------------
def get_cached_lookval(cache_dict, kwargs):
    if 'lookval' in cache_dict:
        return cache_dict['lookval']
    else:
        if 'lookval' in kwargs:
            return kwargs['lookval']
        else:
            return None

# ----------------------- GET PAYER FROM USERCACHE DICT ------------------------
def get_cached_payer(usercache):
    if 'payer' in usercache:
        return usercache['payer']
    else:
        return None

# ------------------------------ CLEAR USER CACHE ------------------------------
def clear_usercache(uid):
    cachename = f"propayui-{uid}"
    cache.delete(cachename)

# --------------------------- GET OR SET USER CACHE ----------------------------
def get_or_set_usercache(uid):
    """
    set cache specific to user and the propay-ui, timeout after 24 hours
    """
    cachename = f"propayui-{uid}"
    usercache = cache.get_or_set(cachename, {}, timeout=60*60*24)
    return usercache

# ----------------------------- UPDATE USER CACHE ------------------------------
def update_usercache(uid, usercache):
    """
    usercache is assumed to be a dictionary, this is written/overwritten completely
    every time usercache is updated
    """
    cachename = f"propayui-{uid}"
    cache.set(cachename, usercache, timeout=60*60*24)

# ------------------------------ TOUCH USER CACHE ------------------------------
def touch_usercache(uid):
    """
    reset expiration timer on user cache
    """
    cachename = f"propayui-{uid}"
    usercache = cache.touch(cachename, timeout=60*60*24)

# ------------------------------------------------------------------------------
