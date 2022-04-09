**documentation is "ProtectPay Application Programming Interface.pdf"**

--------------------------------------------------------------------------------

### to process a transaction once
> /protectpay/Payers/{PayerId}/PaymentMethods/ProcessedTransactions/

- in the json request set `isRecurringPayment` to false.  if setting up for repeated transactions then can be true.


# --- MTV (model template view) ---


# --- setup ---




# --- to do ---
- [ ] test data needs to go somewhere?
- [ ] get_payerID_details search to use single query?  check for email?
- [ ] change all propay function calls to take kwargs instead of positional args
