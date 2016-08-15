import json
import mock
import unittest
import requests_mock
from datetime import datetime

from erply_api import Erply, ErplyAuth, ErplyAPILimitException

try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs


class TestErply(unittest.TestCase):

    CUSTOMER_CODE = '12345'

    def setUp(self):
        self._auth = ErplyAuth(self.CUSTOMER_CODE, 'user', 'pass')

    def test_erply_api_url(self):
        erply = Erply(self._auth)

        assert erply.api_url == 'https://{}.erply.com/api/'.format(self.CUSTOMER_CODE)

    def test_erply_custom_api_url(self):
        url = 'https://foo.com/xxx/'

        erply = Erply(self._auth, erply_api_url=url)

        assert erply.api_url == url


@requests_mock.Mocker()
class TestErplyIntegration(unittest.TestCase):

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


    @mock.patch('erply_api.sleep', return_value=None)
    def test_hourly_limit(self, m, time_sleep):
        _elim_response = json.dumps({'status': {'requestUnixTime': 1470596233, 'responseStatus': 'error', 'recordsInResponse': 0, 'request': 'verifyUser', 'generationTime': 0.00347900390625, 'errorCode': 1002, 'recordsTotal': 0}})
        _customer_1 = json.dumps({"status":{"request":"getCustomers","requestUnixTime":1470506908,"responseStatus":"ok","errorCode":0,"generationTime":0.10754203796387,"recordsTotal":15,"recordsInResponse":1},"records":[{"id":7}]})
        _report_status = json.dumps({'status': {'generationTime': 0.074487924575806, 'recordsInResponse': 1, 'requestUnixTime': 1471021437, 'responseStatus': 'ok', 'errorCode': 0, 'request': 'getSalesReport', 'recordsTotal': 1}, 'records': [{'reportLink': 'https://t1.erply.com/actualreports/123_9aa0b4882da49edb7684e9e5e0144c65.csv'}]})

        m.post('https://{}.erply.com/api/'.format(self.ERPLY_CUSTOMER_CODE), [
            {'text': _elim_response},
            {'text': _customer_1},
            {'text': _elim_response},
            {'text': _customer_1},
        ])
        self.erply._key = 'jVCn2ee69668699820b799fc80bc8a678e235fa3b363'

        # Mark wait_on_limit to True
        self.erply.wait_on_limit = True

        self.erply.getCustomers(**{'recordsOnPage': 1})

        sleep_seconds = (60 * (60 - datetime.fromtimestamp(1470596233).minute)) + 1

        time_sleep.assert_called_once_with(sleep_seconds)

        assert m.call_count == 2
        assert m.request_history[1].text == m.request_history[1].text

        # Try again..
        time_sleep.reset_mock()
        data = self.erply.getSalesReport(getCOGS=0, warehouseID=1, dateStart='2016-06-18', dateEnd='2016-06-18', reportType='SALES_BY_DATE')
        sleep_seconds = (60 * (60 - datetime.fromtimestamp(1470596233).minute)) + 1

        time_sleep.assert_called_once_with(sleep_seconds)

        assert m.call_count == 4
        assert m.request_history[2].text == m.request_history[3].text


    def test_hourly_limit_exception(self, m):
        _elim_response = json.dumps({'status': {'requestUnixTime': 1470596233, 'responseStatus': 'error', 'recordsInResponse': 0, 'request': 'verifyUser', 'generationTime': 0.00347900390625, 'errorCode': 1002, 'recordsTotal': 0}})
        _elim_response_csv = json.dumps({'status': {'request': 'getSalesReport', 'recordsInResponse': 0, 'recordsTotal': 0, 'responseStatus': 'error', 'errorCode': 1002, 'generationTime': 0.0026440620422363, 'requestUnixTime': 1471017803}})

        m.post('https://{}.erply.com/api/'.format(self.ERPLY_CUSTOMER_CODE), [
            {'text': _elim_response},
            {'text': _elim_response_csv},
        ])

        self.erply._key = 'jVCn2ee69668699820b799fc80bc8a678e235fa3b363'

        with self.assertRaises(ErplyAPILimitException) as cm:
            self.erply.getCustomers(**{'recordsOnPage': 1})

        self.assertEqual(cm.exception.server_time, datetime.fromtimestamp(1470596233))

        assert m.call_count == 1

        with self.assertRaises(ErplyAPILimitException) as cm:
            self.erply.getSalesReport(getCOGS=0, warehouseID=1, dateStart='2016-06-18', dateEnd='2016-06-18')

        self.assertEqual(cm.exception.server_time, datetime.fromtimestamp(1471017803))

        assert m.call_count == 2


if __name__ == '__main__':
    unittest.main()
