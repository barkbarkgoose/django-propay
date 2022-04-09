# propay API todos

- [x] refactor logic file (propay.py) so that each function takes and receives JSON data only
  - [ ] refactor hosted transaction function
  - "account" parameter changed to json object
    - the requesting side should use `json.dumps()`

- [x] map URLs/views to each API call function

- [ ] host with website

- [ ] write out UI for ticketing system

- [ ] **search with account number (or name) and give back all the details on that**
  - use `get_payerID_details` to get the _payerID_
  - then use `get_paymentMethod_details(payerID)` to get info on the card

- [ ] **ability to link multiple accounts to the same card**
  - (multiple ExtID pointed to the same payerID)
    - **new card**
      - PUT: `/protectpay/Payers/{PayerID}/PaymentMethods/`
      - call the same URI replacing the _payerID_ each time
        - GET: will just get info without trying to update it

    - **updating**
      - need a lookup to get _PaymentMethodID_ first
      - then repeat URI call replacing _payerID_ and _PaymentMethodID_ each time.
      - POST: `/protectpay/Payers/{PayerID}/PaymentMethods/{PaymentMethodID}/`

  - _could just show any linked accounts and not actually automate card assignment_

- [ ] **transactions**
  - **authorize transaction first**
    - after authorized can void transaction (if testing card)
      - PUT: `/protectpay/VoidedTransactions/`
    - OR capture to request that payment actually go through
      - PUT: `/PaymentMethods/CapturedTransactions/`
