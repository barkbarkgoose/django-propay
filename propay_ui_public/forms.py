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
class HostedTransactionForm(forms.Form):
    PayerAccountId = forms.CharField(
        max_length=16,
        required=True,
        widget=forms.HiddenInput(),
    )
    # --- add to form after submission ---
    # "MerchantProfileId": config.MERCHANT_PROFILE_ID,  # ? faxpipe profile id ?
    # --- amount should be editable
    # "Amount": plan['propay'],
    # "CurrencyCode": "USD",
    # "InvoiceNumber": "Account Signup",
    # "Comment1": plan['description'],
    # "CardHolderNameRequirementType": 1,
    # "SecurityCodeRequirementType": 1,
    # "AvsRequirementType": 1,
    # "StoreCard": True,
    # "OnlyStoreCardOnSuccessfulProcess": False,
    # "CssUrl": config.CSS_URL,
    # "Address1": account.address,
    # "Address2": '',
    # "City": account.city,
    # "Country": 'USA',
    # "Description": '',
    # "Name": account.first_name + ' ' + account.last_name,
    # "State": account.state,
    # "ZipCode": account.zip,
    # "BillerIdentityId": None,
    # "CreationDate": None,
    # "HostedTransactionIdentifier": None,
    # "ReturnURL": return_url,
    # "PaymentTypeId": "0",
    # "Protected": False
    # AuthOnly
    # ProcessCard
    # OnlyStoreCardOnSuccessfulProcess
    pass
