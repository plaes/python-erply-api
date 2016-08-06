import json
import unittest
import requests_mock

from erply_api import Erply, ErplyAuth


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

if __name__ == '__main__':
    unittest.main()
