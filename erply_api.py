# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime
"""
    erply
    ~~~~~

    Simple Python wrapper for Erply API

    :copyright: (c) 2014 by Priit Laes
    :license: BSD, see LICENSE for details.
"""
from contextlib import closing
from datetime import datetime
import csv
import requests


class ErplyException(Exception):
    ###fcdsfsedcxwasd<zxcefdscx fdcx edscxzefdcsx f
    pass

class ErplyAuth(object):

    def __init__(self, code, username, password):
        self.code = code
        self.username = username
        self.password = password

    @property
    def data(self):
        return {'username': self.username,
                'password': self.password}

class Erply(object):

    ERPLY_GET = (
        # TODO: This list is still incomplete
         'getAddresses'
        ,'getAddressTypes'
        ,'getCustomers'
        ,'getCustomerGroups'
        # ,'getDocuments'       Unimplemented from ERPLY side :(
        ,'getEmployees'
        ,'getProducts'
        ,'getProductCategories'
        ,'getProductCostForSpecificAmount'     # untested
        ,'getProductGroups'
        ,'getProductPrices'                    # untested, broken ??
        ,'getProductPriorityGroups'            # untested
        ,'getProductStock'                     # untested
        ,'getProductUnits'
        ,'getPurchaseDocuments'
        ,'getReports'
        ,'getSalesDocuments'
        ,'getServices'
        ,'getWarehouses'
        ,'verifyUser'
    )
    ERPLY_CSV = ('getProductStockCSV', 'getSalesReport')
    ERPLY_POST = ('saveProduct',)

    def __init__(self, auth):
        self.auth = auth
        self._key = None
        self.valid_until = datetime.fromtimestamp(0)

    @property
    def _payload(self):
        return {'clientCode': self.auth.code}

    @property
    def session(self):
        def authenticate():
            response = self.verifyUser(**self.auth.data)
            if response.error:
                print("Authentication failed with code {}".format(response.error))
                raise ValueError
            key = response.fetchone().get('sessionKey', None)
            print (key)
            self._key = key
            self.valid_until = datetime.now() + timedelta(minutes=59, seconds=30)
            return key
        return self._key if self._key else authenticate()

    @property
    def payload(self):
        #print ("now", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print ("valid_until", self.valid_until)
        if not datetime.now() < self.valid_until:
            self._key = None
            self.session
        return dict(sessionKey=self.session, **self._payload)

    @property
    def api_url(self):
        return 'https://{}.erply.com/api/'.format(self.auth.code)

    @property
    def headers(self):
        return { 'Content-Type': 'application/x-www-form-urlencoded'}

    def handle_csv(self, request, *args, **kwargs):
        data = dict(request=request, responseType='CSV')
        data.update(self.payload)
        data.update(**kwargs)
        return ErplyCSVResponse(self, requests.post(self.api_url, data=data, headers=self.headers))

    def handle_get(self, request, _page=None, _response=None, *args, **kwargs):
        _is_bulk = kwargs.pop('_is_bulk', False)
        data = kwargs.copy()
        if _page:
            data['pageNo'] = _page + 1
        if _is_bulk:
            data.update(requestName=request)
            return data
        data.update(request=request)
        data.update(self.payload if request != 'verifyUser' else self._payload)
        r = requests.post(self.api_url, data=data, headers=self.headers)
        #print (r.headers['Date'])
        if _response:
            _response.populate_page(r, _page)
        ErplyResponse.serverDate(self, r)
        return ErplyResponse(self, r, request, _page, *args, **kwargs)

    def handle_post(self, request, *args, **kwargs):
        _is_bulk = kwargs.pop('_is_bulk', False)
        data = kwargs.copy()
        if _is_bulk:
            data.update(requestName=request)
            return data
        data.update(request=request)
        data.update(self.payload)
        r = requests.post(self.api_url, data=data, headers=self.headers)
        print (r.headers['Date'])
        
        
        return ErplyResponse(self, r, request, *args, **kwargs)

    def handle_bulk(self, _requests):
        data = self.payload
        data.update(requests=_requests)
        return ErplyBulkResponse(self, requests.post(self.api_url, data=data))

    def __getattr__(self, attr):
        _attr = None
        _is_bulk = len(attr) > 5 and attr.endswith('_bulk')
        if _is_bulk:
            attr = attr[:-5]
        if attr in self.ERPLY_GET:
            def method(*args, **kwargs):
                _page = kwargs.get('_page', 0)
                _response = kwargs.get('_response', None)
                return self.handle_get(attr, _page, _response, _is_bulk=_is_bulk, *args, **kwargs)
            _attr = method
        elif attr in self.ERPLY_POST:
            def method(*args, **kwargs):
                return self.handle_post(attr, _is_bulk=_is_bulk, *args, **kwargs)
            _attr = method
        elif attr in self.ERPLY_CSV:
            def method(*args, **kwargs):
                return self.handle_csv(attr.replace('CSV', ''), *args, **kwargs)
            _attr = method
        if _attr:
            self.__dict__[attr] = _attr
            return _attr
        raise AttributeError


class ErplyBulkRequest(object):
    def __init__(self, erply,  _json_dumps):
        self.calls = []
        self.erply = erply
        self.json_dumper = _json_dumps

    def attach(self, attr, *args, **kwargs):
        if attr in self.erply.ERPLY_GET or attr in self.erply.ERPLY_POST:
            self.calls.append((getattr(self.erply, '{}_bulk'.format(attr)), args, kwargs))

    def __call__(self,):
        _requests = []
        for n, request in enumerate(self.calls, start=1):
            _call, _args, _kwargs = request
            _kwargs.update(requestID=n)
            _requests.append(_call(*_args, **_kwargs))
        return self.erply.handle_bulk(self.json_dumper(_requests))


class ErplyResponse(object):

    def __init__(self, erply, response, request, page=0, *args, **kwargs):
        self.request = request
        self.erply = erply
        self.error = None
        self.response = response

        # Result pagination setup
        self.page = page
        self.per_page = kwargs.get('recordsOnPage', 20)

        self.kwargs = kwargs

        if response.status_code != requests.codes.ok:
            print ('Request failed with error code {}'.format(response.status_code))
            raise ValueError

        data = response.json()
        status = data.get('status', {})

        if not status:
            print ("Malformed response")
            raise ValueError

        self.error = status.get('errorCode')

        if self.error == 0:
            self.total = status.get('recordsTotal')
            self.records = { page: data.get('records')}
            return

        field = status.get('errorField')
        if field:
            raise ErplyException('{}, field: {}'.format(self.error, field))

        raise ErplyException('{}'.format(self.error))


    def fetchone(self):
        if self.total == 1:
            return self.records[0][0]
        raise ValueError

    def fetch_records(self, page):
        self.erply.handle_get(self.request, _page=page, _response=self, **self.kwargs)

    def populate_page(self, response, page):
        items = response.json().get('records')
        if items:
            assert self.per_page != 0
            self.records[page] = items
    
    def serverDate(self, response):
        unixDate = response.json().get('status').get('requestUnixTime')
        return {'UnixTime': unixDate}
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            raise NotImplementedError
        if self.per_page * key >= self.total:
            raise IndexError
        if key not in self.records:
            self.fetch_records(key)
        return self.records[key]


class ErplyCSVResponse(object):

    def __init__(self, erply, response):
        self.erply = erply

        if response.status_code != requests.codes.ok:
            print ('Request failed with error code {}'.format(response.status_code))
            raise ValueError

        data = response.json()
        status = data.get('status', {})
        if not status:
            print ("Malformed response")
            raise ValueError

        self.error = status.get('errorCode')

        if self.error == 0:
            self.url = data.get('records').pop().get('reportLink')
            self.timestamp = datetime.fromtimestamp(status.get('requestUnixTime'))
            return

        field = status.get('errorField')
        if field:
            raise ErplyException('{}, field: {}'.format(self.error, field))

        raise ErplyException('{}'.format(self.error))


    @property
    def records(self):
        with closing(requests.get(self.url, stream=True)) as f:
            if f.status_code != requests.codes.ok:
                raise ValueError
            # XXX: Check whether we have to make it configurable...
            # XXX: Should we remove header and footer?
            return csv.reader(f.text.splitlines(), delimiter=';')


class ErplyBulkResponse(object):
    def __init__(self, erply, response):
        if response.status_code != requests.codes.ok:
            print ('Request failed with error code {}'.format(response.status_code))
            raise ValueError

        self.data = response.json()
        status = self.data.get('status', {})
        if not status:
            print ("Malformed response")
            raise ValueError

        self.error = status.get('errorCode')
        self._requests = self.data.get('requests')


    @property
    def records(self):
        if self._requests is None:
            raise ValueError
        for el in self._requests:
            _status = el.get('status')
            if _status.get('responseStatus') == 'error':
                print ('Request failed: requestID: {} errorField: {}'.format(
                        _status.get('requestID'),
                        _status.get('errorField'),
                       ))
            else:
                yield el.get('records')
