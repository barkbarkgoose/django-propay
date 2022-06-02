from django.contrib.auth.models import User
from django.db import models

import pdb

# ------------------------------------------------------------------------------
class Singleton(models.Model):
    """
    an abstract singleton class that will always have one (and only one) instance
    made. will insure that pk=1 always

    I got the idea for this here:
        https://www.rootstrap.com/blog/simple-dynamic-settings-for-django/
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Singleton, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        """
        note: load() will return a ProgrammingError if models haven't been migrated
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

# -------------------------------- PAYER CLASS ---------------------------------
class Payer:
    """
    - payer instance, (set/accessed from payer details and subsequent pages)
    - intentionally not stored in db.  Only ever accessed from cache in memory
    """
    def __init__(self, pid, name, id1, id2):
        self.pid = pid
        self.name = name
        self.eid1 = id1
        self.eid2 = id2


    def init_from_request(request):
        """
        initialize a Payer object from request data.  Checks for all init fields
        """
        # --- handle both POST and GET requests ---
        rdata = []
        if request.method == "GET":
            rdata = request.GET
        else:
            rdata = request.POST

        # --- make sure required fields are there ---
        for required in ['payerid', 'payername', 'eid1', 'eid2']:
            if required not in rdata:
                return None

        return Payer(
            rdata['payerid'], rdata['payername'],
            rdata['eid1'], rdata['eid2'],
        )

    @property
    def get_query_url(self):
        url = f"&payerid={self.pid}"
        url += f"&payername={self.name}"
        url += f"&eid1={self.eid1}"
        url += f"&eid2={self.eid2}"
        return url

# ----------------------- BILLING USERS SINGLETON CLASS ------------------------
class BillingUsers(Singleton):
    authorized_users = models.ManyToManyField(User)

    def __str__(self):
        return "Authorized Billing Users List (creating new will overwrite this)"

# ------------------------------------------------------------------------------
