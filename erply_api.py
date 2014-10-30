# -*- coding: utf-8 -*-
"""
    erply
    ~~~~~

    Simple Python wrapper for Erply API

    :copyright: (c) 2014 by Priit Laes
    :license: BSD, see LICENSE for details.
"""


class ErplyAuth(object):

    def __init__(self, code, username, password):
        self.code = code
        self.username = username
        self.password = password


class Erply(object):

    def __init__(self, auth):
        self.auth = auth
        self._key = None

    @property
    def _payload(self):
        return {'clientcode': {}.format(self.auth.code), 'version': '1.0'}

    @property
    def session(self):
        raise NotImplementedError

    @property
    def payload(self):
        p = self._payload
        p.update({'sessionKey': self.session})
        return p

    @property
    def api_url(self):
        return 'https://{}.erply.com/api/'.format(self.auth.code)


class ErplyPagedResult(object):
    pass


class ErplyCSVResult(object):
    pass


class ErplyResult(object):
    pass
