Erply InventoryAPI Python library
=================================

Please note this is API is currently work in progress and might change in future.

Build Status
============
.. image:: https://travis-ci.org/plaes/python-erply-api.svg?branch=master
    :target: https://travis-ci.org/plaes/python-erply-api

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
