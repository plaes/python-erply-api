# -*- coding: utf-8 -*-
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

    ERPLY_GET = ('getCustomerGroups', 'getCustomers', 'getDocuments', \
                 'getProducts', 'getSalesDocuments', 'verifyUser')
    ERPLY_CSV = ('getProductStockCSV',)
    ERPLY_POST = ('saveProduct',)

    def __init__(self, auth):
        self.auth = auth
        self._key = None

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
            self._key = key
            return key
        return self._key if self._key else authenticate()

    @property
    def payload(self):
        return dict(sessionKey=self.session, **self._payload)

    @property
    def api_url(self):
        return 'https://{}.erply.com/api/'.format(self.auth.code)

    @property
    def headers(self):
        return { 'Content-Type': 'application/x-www-form-urlencoded' }

    def handle_csv(self, request, *args, **kwargs):
        data = dict(request=request, responseType='CSV')
        data.update(self.payload)
        data.update(**kwargs)
        return ErplyCSVResponse(self, requests.post(self.api_url, data=data, headers=self.headers))

    def handle_get(self, request, _page=None, _per_page=None, _response=None, *args, **kwargs):
        data = dict(request=request)
        data.update(self.payload if request != 'verifyUser' else self._payload)
        data.update(kwargs)
        if _page:
            data['pageNo'] = _page + 1
        if _per_page:
            data['recordsOnPage'] = _per_page
        r = requests.post(self.api_url, data=data, headers=self.headers)
        if _response:
            _response.update(r, _page)
        return ErplyResponse(self, r, request, _page)

    def handle_post(self, request, *args, **kwargs):
        data = dict(request=request)
        data.update(self.payload)
        data.update(**kwargs)
        r = requests.post(self.api_url, data=data, headers=self.headers)
        return ErplyResponse(self, r, request)

    def __getattr__(self, attr):
        _attr = None
        if attr in self.ERPLY_GET:
            def method(*args, **kwargs):
                _page = kwargs.get('_page', 0)
                _response = kwargs.get('_response', None)
                return self.handle_get(attr, _page, _response, *args, **kwargs)
            _attr = method
        elif attr in self.ERPLY_CSV:
            def method(*args, **kwargs):
                return self.handle_csv(attr.replace('CSV', ''), *args, **kwargs)
            _attr = method
        elif attr in self.ERPLY_POST:
            def method(*args, **kwargs):
                return self.handle_post(attr, *args, **kwargs)
            _attr = method
        if _attr:
            self.__dict__[attr] = _attr
            return _attr
        raise AttributeError


class ErplyResponse(object):

    def __init__(self, erply, response, request, page=0):
        self.request = request
        self.erply = erply
        self.error = None

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
            self.error_desc = None
        elif self.error == 1011:
            self.error_desc = 'Invalid input: {}.'.format(status.get('errorField'))
        elif self.error == 1012:
            self.error_desc = 'Input {} must be unique.'.format(status.get('errorField'))
        else:
            self.error_desc = 'Response error code: {}.'.format(self.error)

        # Paginate results
        self.page = page
        self.total = status.get('recordsTotal')
        self.per_page = status.get('recordsInResponse')

        self.records = { page: data.get('records')}

    def fetchone(self):
        if self.total == 1:
            return self.records[0][0]
        raise ValueError

    def fetch_records(self, page):
        self.erply.handle_get(self.request, _page=page, _per_page=self.per_page, _response=self)

    def update(self, data, page):
        items = data.json().get('records')
        assert len(items) != 0
        self.records[page] = items

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

        self.url = data.get('records').pop().get('reportLink')
        self.timestamp = datetime.fromtimestamp(status.get('requestUnixTime'))

    @property
    def records(self):
        with closing(requests.get(self.url, stream=True)) as f:
            if f.status_code != requests.codes.ok:
                raise ValueError
            reader = csv.reader(f.text.splitlines())
            reader.next()
            return reader
