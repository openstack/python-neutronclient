# Copyright (C) 2013 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc

from mox3 import mox
import requests_mock
import six
import testtools

from neutronclient import client
from neutronclient.common import exceptions
from neutronclient.tests.unit import test_auth
from neutronclient.tests.unit.test_cli20 import MyResp


AUTH_TOKEN = 'test_token'
END_URL = 'test_url'
METHOD = 'GET'
URL = 'http://test.test:1234/v2.0/test'
BODY = 'IAMFAKE'


@six.add_metaclass(abc.ABCMeta)
class TestHTTPClientMixin(object):

    def setUp(self):
        super(TestHTTPClientMixin, self).setUp()

        self.clazz, self.http = self.initialize()
        self.mox = mox.Mox()
        self.addCleanup(self.mox.UnsetStubs)
        self.mox.StubOutWithMock(self.clazz, '_request')

    @abc.abstractmethod
    def initialize(self):
        """Return client class, instance."""

    def _test_headers(self, expected_headers, **kwargs):
        """Test headers."""
        self.clazz._request(URL, METHOD,
                            body=kwargs.get('body'),
                            headers=expected_headers)
        self.mox.ReplayAll()
        self.http.request(URL, METHOD, **kwargs)
        self.mox.VerifyAll()

    def test_headers_without_body(self):
        self._test_headers({'Accept': 'application/json'})

    def test_headers_with_body(self):
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        self._test_headers(headers, body=BODY)

    def test_headers_without_body_with_content_type(self):
        headers = {'Accept': 'application/xml'}
        self._test_headers(headers, content_type='application/xml')

    def test_headers_with_body_with_content_type(self):
        headers = {'Accept': 'application/xml',
                   'Content-Type': 'application/xml'}
        self._test_headers(headers, body=BODY, content_type='application/xml')

    def test_headers_defined_in_headers(self):
        headers = {'Accept': 'application/xml',
                   'Content-Type': 'application/xml'}
        self._test_headers(headers, body=BODY, headers=headers)


class TestSessionClient(TestHTTPClientMixin, testtools.TestCase):

    @requests_mock.Mocker()
    def initialize(self, mrequests):
        session, auth = test_auth.setup_keystone_v2(mrequests)
        return [client.SessionClient,
                client.SessionClient(session=session, auth=auth)]


class TestHTTPClient(TestHTTPClientMixin, testtools.TestCase):

    def initialize(self):
        return [client.HTTPClient,
                client.HTTPClient(token=AUTH_TOKEN, endpoint_url=END_URL)]

    def test_request_error(self):
        self.clazz._request(
            URL, METHOD, body=None, headers=mox.IgnoreArg()
        ).AndRaise(Exception('error msg'))
        self.mox.ReplayAll()

        self.assertRaises(
            exceptions.ConnectionFailed,
            self.http._cs_request,
            URL, METHOD
        )
        self.mox.VerifyAll()

    def test_request_success(self):
        rv_should_be = MyResp(200), 'test content'

        self.clazz._request(
            URL, METHOD, body=None, headers=mox.IgnoreArg()
        ).AndReturn(rv_should_be)
        self.mox.ReplayAll()

        self.assertEqual(rv_should_be, self.http._cs_request(URL, METHOD))
        self.mox.VerifyAll()

    def test_request_unauthorized(self):
        rv_should_be = MyResp(401), 'unauthorized message'
        self.clazz._request(
            URL, METHOD, body=None, headers=mox.IgnoreArg()
        ).AndReturn(rv_should_be)
        self.mox.ReplayAll()

        e = self.assertRaises(exceptions.Unauthorized,
                              self.http._cs_request, URL, METHOD)
        self.assertEqual('unauthorized message', e.message)
        self.mox.VerifyAll()

    def test_request_forbidden_is_returned_to_caller(self):
        rv_should_be = MyResp(403), 'forbidden message'
        self.clazz._request(
            URL, METHOD, body=None, headers=mox.IgnoreArg()
        ).AndReturn(rv_should_be)
        self.mox.ReplayAll()

        self.assertEqual(rv_should_be, self.http._cs_request(URL, METHOD))
        self.mox.VerifyAll()
