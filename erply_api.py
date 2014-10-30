# -*- coding: utf-8 -*-
"""
    erply
    ~~~~~

    Simple Python wrapper for Erply API

    :copyright: (c) 2014 by Priit Laes
    :license: BSD, see LICENSE for details.
"""
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

    ERPLY_GET = ('getProducts', 'verifyUser')

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
            key = response.records.pop().get('sessionKey', None)
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

    def handle_get(self, request, _page=None, _response=None, *args, **kwargs):
        data = dict(request=request)
        data.update(self.payload if request != 'verifyUser' else self._payload)
        data.update(kwargs)
        if _page:
            data['pageNo'] = _page + 1
        r = requests.post(self.api_url, data=data, headers=self.headers)
        if _response:
            _response.update(r, _page)
        return ErplyResponse(self, r, _page)

    def __getattr__(self, attr):
        if attr in self.ERPLY_GET:
            def method(*args, **kwargs):
                _page = kwargs.get('_page', None)
                _response = kwargs.get('_response', None)
                return self.handle_get(attr, _page, _response, *args, **kwargs)
            self.__dict__[attr] = method
            return method
        raise AttributeError


class ErplyResponse(object):

    def __init__(self, erply, r, page):
        self.erply = erply
        self.error = None

        if r.status_code != requests.codes.ok:
            print ('Request failed with error code {}'.format(r.status_code))
            raise ValueError

        data = r.json()
        status = data.get('status', {})

        if not status:
            print ("Malformed response")
            raise ValueError

        self.status = status.get('responseStatus')
        self.error = status.get('errorCode')

        self.records = data.get('records')

class ErplyPagedResult(object):
    pass


class ErplyCSVResult(object):
    pass


class ErplyResult(object):
    pass
