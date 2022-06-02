import pdb, re

from datetime import date
from django import forms
from phonenumber_field.formfields import PhoneNumberField

THISYEAR = date.today().year

MONTH_CHOICES = [
    ("01", "01"), ("02", "02"), ("03", "03"), ("04", "04"),
    ("05", "05"), ("06", "06"), ("07", "07"), ("08", "08"),
    ("09", "09"), ("10", "10"), ("11", "11"), ("12", "12"),
]

STATE_OPTIONS = [
    ('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'),
    ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DC', 'DC'),
    ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'),
    ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'),
    ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'),
    ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'),
    ('MS', 'MS'), ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'),
    ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'),
    ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'),
    ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'),
    ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'),
    ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'),
    ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY'),
]

RE_PHONEPATTERN = "^\({0,1}\d{3}\){0,1}\s{0,1}-{0,1}\d{3}-{0,1}\d{4}$"

# -------------------------- HOSTED TRANSACTION FORM ---------------------------
class HostedTransactionInstanceForm(forms.Form):
    # # --- required ---
    #
    # Amount
    # AuthOnly
    # AvsRequirementType
    # CardHolderNameRequirementType
    # CurrencyCode
    # MerchantProfileId
    # OnlyStoreCardOnSuccessfulProcess
    # PaymentTypeId
    # PayerId
    # ProcessCard
    # SecurityCodeRequirementType
    # StoreCard
    # ReturnUrl  # should be hidden
    #
    # # --- optional ---
    # InvoiceNumber
    # CssUrl
    # Comment1
    # Address1
    # Address2
    # City
    # Country
    # Description
    # Name
    # State
    # ZipCode
    # TransactionMerchantDescriptor
    pass
