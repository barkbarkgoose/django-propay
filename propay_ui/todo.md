# overall goals
- [ ] draw out all views/functions for ui
  - [ ] determine if function call should refresh entire page or only part of it

- [ ] figure out if want single function to handle all api connection requests
      for data or if each view should do that
  - (will depend on if each page is being loaded with info in uri or not)

-----
### views to figure out:
**need to determine which calls depend on return info from another**

    what info should be in URI and what should be handled inside of request ??

- [ ] voidtransaction
- [ ] createpayer
- [ ] payerdetails
  - [ ] updatepayer
  - [ ] deletepayer
  - [ ] createpaymethod
  - [ ] paymethoddetails
    - [ ] updatepaymethod
    - [ ] deletepaymethod
    - [ ] validatecard


-----

# cacheing

- payer_search
  - get lookval from cache if available, otherwise kwargs
  - form submission gives new lookval in `form.cleaned_data`
  - cache new lookval (this is where it should be first set)

-----
