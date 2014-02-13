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

from mox3 import mox
import testtools

from neutronclient.client import HTTPClient
from neutronclient.common import exceptions
from neutronclient.tests.unit.test_cli20 import MyResp


AUTH_TOKEN = 'test_token'
END_URL = 'test_url'
METHOD = 'GET'
URL = 'http://test.test:1234/v2.0/test'


class TestHTTPClient(testtools.TestCase):
    def setUp(self):
        super(TestHTTPClient, self).setUp()

        self.mox = mox.Mox()
        self.mox.StubOutWithMock(HTTPClient, 'request')
        self.addCleanup(self.mox.UnsetStubs)

        self.http = HTTPClient(token=AUTH_TOKEN, endpoint_url=END_URL)

    def test_request_error(self):
        HTTPClient.request(
            URL, METHOD, headers=mox.IgnoreArg()
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

        HTTPClient.request(
            URL, METHOD, headers=mox.IgnoreArg()
        ).AndReturn(rv_should_be)
        self.mox.ReplayAll()

        self.assertEqual(rv_should_be, self.http._cs_request(URL, METHOD))
        self.mox.VerifyAll()

    def test_request_unauthorized(self):
        rv_should_be = MyResp(401), 'unauthorized message'
        HTTPClient.request(
            URL, METHOD, headers=mox.IgnoreArg()
        ).AndReturn(rv_should_be)
        self.mox.ReplayAll()

        e = self.assertRaises(exceptions.Unauthorized,
                              self.http._cs_request, URL, METHOD)
        self.assertEqual('unauthorized message', e.message)
        self.mox.VerifyAll()

    def test_request_forbidden_is_returned_to_caller(self):
        rv_should_be = MyResp(403), 'forbidden message'
        HTTPClient.request(
            URL, METHOD, headers=mox.IgnoreArg()
        ).AndReturn(rv_should_be)
        self.mox.ReplayAll()

        self.assertEqual(rv_should_be, self.http._cs_request(URL, METHOD))
        self.mox.VerifyAll()
