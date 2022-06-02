import pdb, uuid

from django.core.management.base import BaseCommand, CommandError

from jake_template.django_things import customlog
from support import controller
from propay_api.tests import json_test

class Command(BaseCommand):
    def handle(self, *args, **options):
        json_test()
