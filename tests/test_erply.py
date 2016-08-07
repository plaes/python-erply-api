import json
import mock
import unittest
import requests_mock
from datetime import datetime

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
        _ware_response = json.dumps({"status":{"request":"getWarehouses","requestUnixTime":1470473993,"responseStatus":"ok","errorCode":0,"generationTime":0.054569959640503,"recordsTotal":3,"recordsInResponse":3},"records":[{"warehouseID":"1"},{"warehouseID":"2"},{"warehouseID":"3"}]})
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
        _customer_1 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506908,"responseStatus":"ok","errorCode":0,"generationTime":0.10754203796387,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":7}]})
        _customer_2 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506909,"responseStatus":"ok","errorCode":0,"generationTime":0.10276508331299,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":14}]})

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
        _customer_1 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506908,"responseStatus":"ok","errorCode":0,"generationTime":0.10754203796387,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":7}]})
        _customer_2 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506909,"responseStatus":"ok","errorCode":0,"generationTime":0.10276508331299,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":14}]})

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
        # 2 calls: auth + request
        assert m.call_count == 2

        assert len(r.records[0]) == 1

        # Fetch next page
        next(it)
        # 3 calls: request fail + auth + re-request
        assert m.call_count == 5

        assert 'recordsOnPage' in m.request_history[2].text
        assert m.request_history[2].text == m.request_history[4].text

        assert len(r.records[1]) == 1


    @mock.patch('time.sleep', return_value=None)
    def test_hourly_limit(self, m, time_sleep):
        _elim_response = json.dumps({'status': {'requestUnixTime': 1470596233, 'responseStatus': 'error', 'recordsInResponse': 0, 'request': 'verifyUser', 'generationTime': 0.00347900390625, 'errorCode': 1002, 'recordsTotal': 0}})
        _auth_response = json.dumps({"status":{"request":"verifyUser","requestUnixTime":1470506907,"responseStatus":"ok","errorCode":0,"generationTime":0.046638011932373,"recordsTotal":1,"recordsInResponse":1},"records":[{"userID":"6","userName":"demo","employeeID":"4","employeeName":"Clara Smith","groupID":"7","groupName":"sales representatives","sessionKey":"jVCn2ee69668699820b799fc80bc8a678e235fa3b363","sessionLength":3600,"loginUrl":"https:\/\/demo.erply.com\/eng\/","berlinPOSVersion":"3.17.2","berlinPOSAssetsURL":"http:\/\/assets.erply.com\/berlin\/","epsiURL":"https:\/\/app.erply.com\/epsi\/EPSI.jnlp"}]})
        _customer_1 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506908,"responseStatus":"ok","errorCode":0,"generationTime":0.10754203796387,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":7}]})

        m.post('https://{}.erply.com/api/'.format(self.ERPLY_CUSTOMER_CODE), [
            {'text': _elim_response},
            {'text': _auth_response},
            {'text': _customer_1},
        ])

        self.erply.getCustomers(**{'recordsOnPage': 1})

        server_time = (60 * (60 - datetime.fromtimestamp(1470596233).minute)) + 1

        time_sleep.assert_called_once_with(server_time)


if __name__ == '__main__':
    unittest.main()
