Erply InventoryAPI Python library
=================================

Please note this is API is currently work in progress and might change in future.
Nevertheless, it has already been used in various scenarios in production:

* Daily sync functionality for managing inventory in multiple brick and mortar
  stores with webshop and custom backoffice software.
* Migration utility for transferring multiple years of data from Erply to Odoo.

Usage
=====
.. code:: python

    from erply_api import Erply, ErplyAuth

    ERPLY_CUSTOMER_CODE = "eng"
    ERPLY_USERNAME = "demo"
    ERPLY_PASSWORD = "demouser"

    auth = ErplyAuth(ERPLY_CUSTOMER_CODE, ERPLY_USERNAME, ERPLY_PASSWORD)
    erply = Erply(auth)
    response = erply.getProducts()
    print (response.total)
    # Iterate over automatically paginated results
    for page in response:
        for product in page:
            print (product)

Donate
======

If you need some new functionality or help with a project don't hesitate
to ask. Or, if you already found this library helpful - you can contribute
via `Github Sponsors <https://github.com/sponsors/plaes>`_.
