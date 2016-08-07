import json
import unittest
import requests_mock

from erply_api import Erply, ErplyAuth

try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs



@requests_mock.Mocker()
class TestErply(unittest.TestCase):

    # Default Erply Demo account credentials
    ERPLY_CUSTOMER_CODE = 'eng'
    ERPLY_USERNAME = 'demo'
    ERPLY_PASSWORD = 'demouser'

    def setUp(self):
        self._auth = ErplyAuth(self.ERPLY_CUSTOMER_CODE, self.ERPLY_USERNAME, self.ERPLY_PASSWORD)
        self.erply = Erply(self._auth)

    def test_erply_reauth(self, m):
        _auth_response = json.dumps({"status":{"request":"verifyUser","requestUnixTime":1470473993,"responseStatus":"ok","errorCode":0,"generationTime":0.036508083343506,"recordsTotal":1,"recordsInResponse":1},"records":[{"userID":"6","userName":"demo","employeeID":"4","employeeName":"Clara Smith","groupID":"7","groupName":"sales representatives","sessionKey":"hCmu694a3fd6758786f3da68fc4e9a72f7404b2216c0","sessionLength":5,"loginUrl":"https:\/\/demo.erply.com\/eng\/","berlinPOSVersion":"3.17.2","berlinPOSAssetsURL":"http:\/\/assets.erply.com\/berlin\/","epsiURL":"https:\/\/app.erply.com\/epsi\/EPSI.jnlp"}]})
        _ware_response = json.dumps({"status":{"request":"getWarehouses","requestUnixTime":1470473993,"responseStatus":"ok","errorCode":0,"generationTime":0.054569959640503,"recordsTotal":3,"recordsInResponse":3},"records":[{"warehouseID":"1","pricelistID":"0","pricelistID2":"0","pricelistID3":"0","pricelistID4":0,"pricelistID5":0,"name":"Main warehouse","code":"","addressID":0,"address":"","street":"","address2":"","city":"","state":"","country":"","ZIPcode":"","companyName":"","companyCode":"","companyVatNumber":"","phone":"","fax":"","email":"","website":"","bankName":"","bankAccountNumber":"","iban":"","swift":"","usesLocalQuickButtons":0,"defaultCustomerGroupID":0,"isOfflineInventory":0},{"warehouseID":"2","pricelistID":"0","pricelistID2":"0","pricelistID3":"0","pricelistID4":0,"pricelistID5":0,"name":"5th Avenue","code":"","addressID":0,"address":"","street":"","address2":"","city":"","state":"","country":"","ZIPcode":"","companyName":"","companyCode":"","companyVatNumber":"","phone":"","fax":"","email":"","website":"","bankName":"","bankAccountNumber":"","iban":"","swift":"","usesLocalQuickButtons":0,"defaultCustomerGroupID":0,"isOfflineInventory":0},{"warehouseID":"3","pricelistID":"0","pricelistID2":"0","pricelistID3":"0","pricelistID4":0,"pricelistID5":0,"name":"6th Avenue","code":"","addressID":0,"address":"","street":"","address2":"","city":"","state":"","country":"","ZIPcode":"","companyName":"","companyCode":"","companyVatNumber":"","phone":"","fax":"","email":"","website":"","bankName":"","bankAccountNumber":"","iban":"","swift":"","usesLocalQuickButtons":0,"defaultCustomerGroupID":0,"isOfflineInventory":0}]})
        _sexp_response = json.dumps({"status":{"request":"getWarehouses","requestUnixTime":1470474000,"responseStatus":"error","errorCode":1054,"generationTime":0.0036911964416504,"recordsTotal":0,"recordsInResponse":0}})
        m.post('https://{}.erply.com/api/'.format(self.ERPLY_CUSTOMER_CODE), [
            {'text': _auth_response},
            {'text': _ware_response},
            # Initial session expired response
            {'text': _sexp_response},
            # Re-auth again
            {'text': _auth_response},
            {'text': _ware_response},
        ])
        self.erply.getWarehouses()
        assert m.call_count == 2
        self.erply.getWarehouses()
        assert m.call_count == 5

        r = self.erply.getWarehouses()
        assert r.total == 3

        # Third call should only increase call count by 1
        assert m.call_count == 6

    def test_auto_result_paginator(self, m):
        _auth_response = json.dumps({"status":{"request":"verifyUser","requestUnixTime":1470506907,"responseStatus":"ok","errorCode":0,"generationTime":0.046638011932373,"recordsTotal":1,"recordsInResponse":1},"records":[{"userID":"6","userName":"demo","employeeID":"4","employeeName":"Clara Smith","groupID":"7","groupName":"sales representatives","sessionKey":"jVCn2ee69668699820b799fc80bc8a678e235fa3b363","sessionLength":3600,"loginUrl":"https:\/\/demo.erply.com\/eng\/","berlinPOSVersion":"3.17.2","berlinPOSAssetsURL":"http:\/\/assets.erply.com\/berlin\/","epsiURL":"https:\/\/app.erply.com\/epsi\/EPSI.jnlp"}]})
        _customer_1 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506908,"responseStatus":"ok","errorCode":0,"generationTime":0.10754203796387,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":7,"customerID":7,"type_id":"0","fullName":"Baker, Mary","companyName":"","firstName":"Mary","lastName":"Baker","groupID":18,"payerID":0,"phone":"4321-50826-23","mobile":"","email":"mary@baker.com","fax":"","code":"","birthday":"1969-10-17","integrationCode":"","flagStatus":0,"colorStatus":"blue","credit":1000,"salesBlocked":0,"referenceNumber":"","customerCardNumber":"","groupName":"One-time Customers","customerType":"PERSON","address":"","street":"","address2":"","city":"","postalCode":"","country":"","state":"","isPOSDefaultCustomer":0,"euCustomerType":"DOMESTIC","lastModifierUsername":"mariliis","lastModifierEmployeeID":0,"taxExempt":0,"paysViaFactoring":0,"rewardPoints":0,"twitterID":"","facebookName":"","creditCardLastNumbers":"","deliveryTypeID":0,"image":"","rewardPointsDisabled":0,"posCouponsDisabled":0,"emailOptOut":0,"signUpStoreID":0,"homeStoreID":0,"gender":""}]})
        _customer_2 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506909,"responseStatus":"ok","errorCode":0,"generationTime":0.10276508331299,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":14,"customerID":14,"type_id":"32","fullName":"FineClothing","companyName":"FineClothing","firstName":"","lastName":"","groupID":17,"payerID":0,"phone":"","mobile":"","email":"","fax":"","code":"","birthday":"","integrationCode":"","flagStatus":1,"colorStatus":"red","credit":0,"salesBlocked":0,"referenceNumber":"","customerCardNumber":"","groupName":"Loyal Customers","customerType":"COMPANY","address":"2 Sanders St, Tulsa, OK 45011","street":"2 Sanders St","address2":"","city":"Tulsa","postalCode":"45011","country":"","state":"OK","isPOSDefaultCustomer":0,"euCustomerType":"DOMESTIC","lastModifierUsername":"mariliis","lastModifierEmployeeID":0,"taxExempt":0,"paysViaFactoring":0,"rewardPoints":0,"twitterID":"","facebookName":"","creditCardLastNumbers":"","deliveryTypeID":0,"image":"","rewardPointsDisabled":0,"posCouponsDisabled":0,"emailOptOut":0,"signUpStoreID":0,"homeStoreID":0,"gender":""}]})

        m.post('https://{}.erply.com/api/'.format(self.ERPLY_CUSTOMER_CODE), [
            {'text': _auth_response},
            {'text': _customer_1},
            {'text': _customer_2},
        ])

        r = self.erply.getCustomers(**{'recordsOnPage': 1})
        assert r.total == 15

        # Fetch 2 first elements
        it = iter(r)
        next(it)
        next(it)
        assert m.call_count == 3

        qs = parse_qs(m.request_history[2].text)
        assert qs.get('recordsOnPage') == ['1']
        assert qs.get('pageNo') == ['2']

    def test_reauth_parameters(self, m):
        _auth_response = json.dumps({"status":{"request":"verifyUser","requestUnixTime":1470506907,"responseStatus":"ok","errorCode":0,"generationTime":0.046638011932373,"recordsTotal":1,"recordsInResponse":1},"records":[{"userID":"6","userName":"demo","employeeID":"4","employeeName":"Clara Smith","groupID":"7","groupName":"sales representatives","sessionKey":"jVCn2ee69668699820b799fc80bc8a678e235fa3b363","sessionLength":3600,"loginUrl":"https:\/\/demo.erply.com\/eng\/","berlinPOSVersion":"3.17.2","berlinPOSAssetsURL":"http:\/\/assets.erply.com\/berlin\/","epsiURL":"https:\/\/app.erply.com\/epsi\/EPSI.jnlp"}]})
        _serr_response = json.dumps({"status":{"request":"getProducts","requestUnixTime":1470474000,"responseStatus":"error","errorCode":1054,"generationTime":0.0036911964416504,"recordsTotal":0,"recordsInResponse":0}})
        _customer_1 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506908,"responseStatus":"ok","errorCode":0,"generationTime":0.10754203796387,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":7,"customerID":7,"type_id":"0","fullName":"Baker, Mary","companyName":"","firstName":"Mary","lastName":"Baker","groupID":18,"payerID":0,"phone":"4321-50826-23","mobile":"","email":"mary@baker.com","fax":"","code":"","birthday":"1969-10-17","integrationCode":"","flagStatus":0,"colorStatus":"blue","credit":1000,"salesBlocked":0,"referenceNumber":"","customerCardNumber":"","groupName":"One-time Customers","customerType":"PERSON","address":"","street":"","address2":"","city":"","postalCode":"","country":"","state":"","isPOSDefaultCustomer":0,"euCustomerType":"DOMESTIC","lastModifierUsername":"mariliis","lastModifierEmployeeID":0,"taxExempt":0,"paysViaFactoring":0,"rewardPoints":0,"twitterID":"","facebookName":"","creditCardLastNumbers":"","deliveryTypeID":0,"image":"","rewardPointsDisabled":0,"posCouponsDisabled":0,"emailOptOut":0,"signUpStoreID":0,"homeStoreID":0,"gender":""}]})
        _customer_2 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506909,"responseStatus":"ok","errorCode":0,"generationTime":0.10276508331299,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":14,"customerID":14,"type_id":"32","fullName":"FineClothing","companyName":"FineClothing","firstName":"","lastName":"","groupID":17,"payerID":0,"phone":"","mobile":"","email":"","fax":"","code":"","birthday":"","integrationCode":"","flagStatus":1,"colorStatus":"red","credit":0,"salesBlocked":0,"referenceNumber":"","customerCardNumber":"","groupName":"Loyal Customers","customerType":"COMPANY","address":"2 Sanders St, Tulsa, OK 45011","street":"2 Sanders St","address2":"","city":"Tulsa","postalCode":"45011","country":"","state":"OK","isPOSDefaultCustomer":0,"euCustomerType":"DOMESTIC","lastModifierUsername":"mariliis","lastModifierEmployeeID":0,"taxExempt":0,"paysViaFactoring":0,"rewardPoints":0,"twitterID":"","facebookName":"","creditCardLastNumbers":"","deliveryTypeID":0,"image":"","rewardPointsDisabled":0,"posCouponsDisabled":0,"emailOptOut":0,"signUpStoreID":0,"homeStoreID":0,"gender":""}]})

        m.post('https://{}.erply.com/api/'.format(self.ERPLY_CUSTOMER_CODE), [
            {'text': _auth_response},
            {'text': _customer_1},
            {'text': _serr_response},
            {'text': _auth_response},
            {'text': _customer_2},
        ])
        r = self.erply.getCustomers(**{'recordsOnPage': 1})

        it = iter(r)
        next(it)
        assert m.call_count == 2

        next(it)
        assert m.call_count == 5

        assert 'recordsOnPage' in m.request_history[2].text
        assert m.request_history[2].text == m.request_history[4].text


if __name__ == '__main__':
    unittest.main()
