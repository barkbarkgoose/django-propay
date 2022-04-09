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

# ------------------------------- CARD ADD FORM --------------------------------
class CardAddForm(forms.Form):
    # --- hidden input ---
    PayerAccountId = forms.CharField(
        max_length=16,
        required=True,
        widget=forms.HiddenInput(),
    )
    DuplicateAction = forms.CharField(
        max_length=9,
        required=True,
        widget=forms.HiddenInput(),
    )

    # --- required and optional input ---
    AccountName = forms.CharField(
        max_length=50,
        required=True,
        label="Name (as it appears on card/account)"
    )
    TelephoneNumber = forms.RegexField(
        required=False,
        regex = re.compile(RE_PHONEPATTERN),
    )
    AccountNumber = forms.DecimalField(
        max_digits=16,
        decimal_places=0,
        required=True,
        label="Card/Account Number"
    )
    ### ExpirationDate: MMYY
    ExpirationMonth = forms.ChoiceField(
        required=True,
        choices=MONTH_CHOICES,
    )
    ExpirationYear = forms.ChoiceField(
        required=True,
        ### choices ex: ("22", "2022")
        choices=[
            (f"{year}"[-2:], f"{year}") for year in range(THISYEAR, THISYEAR+10)
        ]
    )
    PaymentMethodType = forms.ChoiceField(
        required=True,
        label="Card Type",
        choices=[
            ('AMEX', 'AMEX (starts with "3")'),
            ('Visa', 'Visa (starts with "4")'),
            ('MasterCard', 'MasterCard ( starts with "5")'),
            ('Discover', 'Discover (starts with "6")'),
            # --- other propay options available, not used by default ---
            # ('DinersClub', 'DinersClub'),
            # ('JCB', 'JCB'),
            # ('ProPayToProPay', 'ProPayToProPay'),
            # ('Checking', 'Checking'),
            # ('Savings', 'Savings'),
            # ('Maestro', 'Maestro'), # (Only for use when connecting to PayVision Gateway)
            # ('CarteBancaire', 'CarteBancaire'), # (Only for use when connecting to PayVision Gateway)
            # ('SEPA', 'SEPA'), # (Only for use when connecting to PayVision Gateway
        ],
    )
    Priority = forms.RegexField(
        required=False,
        label = "Card Processing Priority",
        regex = re.compile("^[0-9]{1}"),
    )
    Description = forms.CharField(
        max_length=25,
        required=False,
    )
    Address1 = forms.CharField(
        max_length=50,
        required=True,
    )
    Address2 = forms.CharField(
        max_length=50,
        required=False,
    )
    Address3 = forms.CharField(
        max_length=50,
        required=False,
    )
    City = forms.CharField(
        max_length=50,
        required=True,
    )
    State  = forms.ChoiceField(
        required=True,
        choices=STATE_OPTIONS,
    )
    ZipCode = forms.DecimalField(
        max_digits=5,
        decimal_places=0,
        required=True,
    )
    Country = forms.ChoiceField(
        required=True,
        choices=[
            ("USA", "United States"),
        ]
    )
    # --- ACH processing fields ---
    # BankNumber = forms.CharField(
    #     max_length=50,
    #     required=False,
    # )
    # AccountCountryCode   ### ACH method only
    # Priority
    # Protected   # maybe don't add this one?  not sure if we are the 'payer' (see docs)

    def clean(self):
        super().clean()
        if self.is_valid():

            # --- get ExpirationDate and remove Month/Year ---
            m = self.cleaned_data.get("ExpirationMonth")
            y = self.cleaned_data.get("ExpirationYear")
            self.cleaned_data['ExpirationDate'] = f"{m}{y}"
            self.cleaned_data.pop('ExpirationMonth')
            self.cleaned_data.pop('ExpirationYear')

            # --- check for valid card length ---
            card_tp = self.cleaned_data.get("PaymentMethodType")
            card_no = self.cleaned_data.get("AccountNumber")
            if card_tp == "AMEX":
                if len(str(card_no)) != 15:
                    self.add_error(
                        "AccountNumber",
                        "AMEX cards should be 15 digits in length",
                    )
            else:
                if len(str(card_no)) != 16:
                    self.add_error(
                        "AccountNumber",
                        "Visa, MasterCard, and Discover cards should be 16 digits in length",
                    )

            # --- make Decimals strngs ---
            self.cleaned_data['AccountNumber'] = str(card_no)
            self.cleaned_data['ZipCode'] = str(self.cleaned_data.get('ZipCode'))

            # --- create sub-dictionary for BillingInformation ---
            billing_keys = [
                'Address1', 'Address2', 'Address3', 'City', 'Country', 'State',
                'TelephoneNumber', 'ZipCode',
            ]
            billing_dict = {}
            for key in billing_keys:
                billing_dict[key] = self.cleaned_data.pop(key)

            self.cleaned_data['BillingInformation'] = billing_dict
        # endif

# ------------------------------ CARD EDIT FORM --------------------------------
class CardEditForm(forms.Form):
    # --- hidden input ---
    PayerAccountId = forms.CharField(
        max_length=16,
        required=True,
        widget=forms.HiddenInput(),
    )
    PaymentMethodId = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.HiddenInput(),
    )
    # --- required and optional input ---
    AccountName = forms.CharField(
        max_length=50,
        required=True,
        label="Name (as it appears on card/account)"
    )
    TelephoneNumber = forms.RegexField(
        required=False,
        regex = re.compile(RE_PHONEPATTERN),
    )
    ### ExpirationDate: MMYY
    ExpirationMonth = forms.ChoiceField(
        required=True,
        choices=MONTH_CHOICES,
    )
    ExpirationYear = forms.ChoiceField(
        required=True,
        ### choices ex: ("22", "2022")
        choices=[
            (f"{year}"[-2:], f"{year}") for year in range(THISYEAR, THISYEAR+10)
        ]
    )
    Description = forms.CharField(
        max_length=25,
        required=False,
    )
    Address1 = forms.CharField(
        max_length=50,
        required=True,
    )
    Address2 = forms.CharField(
        max_length=50,
        required=False,
    )
    Address3 = forms.CharField(
        max_length=50,
        required=False,
    )
    City = forms.CharField(
        max_length=50,
        required=True,
    )
    State  = forms.ChoiceField(
        required=True,
        choices=STATE_OPTIONS,
    )
    ZipCode = forms.DecimalField(
        max_digits=5,
        decimal_places=0,
        required=True,
    )
    Country = forms.ChoiceField(
        required=True,
        choices=[
            ("USA", "United States"),
        ]
    )

    def clean(self):
        super().clean()
        if self.is_valid():

            # --- get ExpirationDate and remove Month/Year ---
            m = self.cleaned_data.get("ExpirationMonth")
            y = self.cleaned_data.get("ExpirationYear")
            self.cleaned_data['ExpirationDate'] = f"{m}{y}"
            self.cleaned_data.pop('ExpirationMonth')
            self.cleaned_data.pop('ExpirationYear')

            # --- make Decimals strngs ---
            self.cleaned_data['ZipCode'] = str(self.cleaned_data.get('ZipCode'))

            # --- create sub-dictionary for BillingInformation ---
            billing_keys = [
                'Address1', 'Address2', 'Address3', 'City', 'Country', 'State',
                'TelephoneNumber', 'ZipCode',
            ]
            billing_dict = {}
            for key in billing_keys:
                billing_dict[key] = self.cleaned_data.pop(key)

            self.cleaned_data['BillingInformation'] = billing_dict
        # endif

# -------------------------------- LOOKUP FORM ---------------------------------
class LookupForm(forms.Form):
    lookval = forms.CharField(
        max_length=50,
        label="Lookup Value",
    )

# ----------------------------- PAYER CREATE FORM ------------------------------
class PayerCreateForm(forms.Form):
    """
    used to create AND update a Payer
    NOTE:
        - largest length of any field truncated at 50 by Propay
    """
    Name = forms.CharField(
        max_length=50,
        required = True,
    )
    ExternalId1 = forms.CharField(
        max_length = 50,
        required = True,
        label = "Account Number (must be unique to payer)",
    )
    ExternalId2 = forms.CharField(
        max_length = 50,
        required = False,
    )
    EmailAddress = forms.EmailField(
        max_length = 50,
        required = False,
    )

# ----------------------------- PAYER UPDATE FORM ------------------------------
class PayerUpdateForm(forms.Form):
    """
    used to create AND update a Payer
    NOTE:
        - largest length of any field truncated at 50 by Propay
    """
    Name = forms.CharField(
        max_length=50,
        required = True,
    )
    ExternalId1 = forms.CharField(
        max_length = 50,
        required = True,
        label = "Account Number (must be unique to payer)",
    )
    ExternalId2 = forms.CharField(
        max_length = 50,
        required = False,
    )

# -------------------------- TRANSACTION LOOKUP FORM ---------------------------
class TransactionLookupForm(forms.Form):
    lookval = forms.CharField(
        max_length=50,
        label="Transaction ID",
    )
#
