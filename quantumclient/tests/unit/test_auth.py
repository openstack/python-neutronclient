# Copyright 2012 NEC Corporation
# All Rights Reserved
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
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import mox
from mox import ContainsKeyValue, IsA, StrContains
import unittest

import httplib2
import json
import uuid

from quantumclient.common import exceptions
from quantumclient.client import HTTPClient


USERNAME = 'testuser'
TENANT_NAME = 'testtenant'
PASSWORD = 'password'
AUTH_URL = 'authurl'
ENDPOINT_URL = 'localurl'
TOKEN = 'tokentoken'
REGION = 'RegionTest'

KS_TOKEN_RESULT = {
    'access': {
        'token': {'id': TOKEN,
                  'expires': '2012-08-11T07:49:01Z',
                  'tenant': {'id': str(uuid.uuid1())}},
        'user': {'id': str(uuid.uuid1())},
        'serviceCatalog': [
            {'endpoints_links': [],
             'endpoints': [{'adminURL': ENDPOINT_URL,
                            'internalURL': ENDPOINT_URL,
                            'publicURL': ENDPOINT_URL,
                            'region': REGION}],
             'type': 'network',
             'name': 'Quantum Service'}
        ]
    }
}


class CLITestAuthKeystone(unittest.TestCase):

    def setUp(self):
        """Prepare the test environment"""
        self.mox = mox.Mox()
        self.client = HTTPClient(username=USERNAME, tenant_name=TENANT_NAME,
                                 password=PASSWORD, auth_url=AUTH_URL,
                                 region_name=REGION)

    def tearDown(self):
        """Clear the test environment"""
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def test_get_token(self):
        self.mox.StubOutWithMock(self.client, "request")

        res200 = self.mox.CreateMock(httplib2.Response)
        res200.status = 200

        self.client.request(AUTH_URL + '/tokens', 'POST',
                            body=IsA(str), headers=IsA(dict)).\
            AndReturn((res200, json.dumps(KS_TOKEN_RESULT)))
        self.client.request(StrContains(ENDPOINT_URL + '/resource'), 'GET',
                            headers=ContainsKeyValue('X-Auth-Token', TOKEN)).\
            AndReturn((res200, ''))
        self.mox.ReplayAll()

        self.client.do_request('/resource', 'GET')
        self.assertEqual(self.client.endpoint_url, ENDPOINT_URL)
        self.assertEqual(self.client.auth_token, TOKEN)
        self.assertEqual(self.client.token_retrieved, True)

    def test_already_token_retrieved(self):
        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN
        self.client.endpoint_url = ENDPOINT_URL
        self.client.token_retrieved = True

        res200 = self.mox.CreateMock(httplib2.Response)
        res200.status = 200

        self.client.request(StrContains(ENDPOINT_URL + '/resource'), 'GET',
                            headers=ContainsKeyValue('X-Auth-Token', TOKEN)).\
            AndReturn((res200, ''))
        self.mox.ReplayAll()

        self.client.do_request('/resource', 'GET')

    def test_refresh_token(self):
        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN
        self.client.endpoint_url = ENDPOINT_URL
        self.client.token_retrieved = True

        res200 = self.mox.CreateMock(httplib2.Response)
        res200.status = 200
        res401 = self.mox.CreateMock(httplib2.Response)
        res401.status = 401

        # If a token is expired, quantum server retruns 401
        self.client.request(StrContains(ENDPOINT_URL + '/resource'), 'GET',
                            headers=ContainsKeyValue('X-Auth-Token', TOKEN)).\
            AndReturn((res401, ''))
        self.client.request(AUTH_URL + '/tokens', 'POST',
                            body=IsA(str), headers=IsA(dict)).\
            AndReturn((res200, json.dumps(KS_TOKEN_RESULT)))
        self.client.request(StrContains(ENDPOINT_URL + '/resource'), 'GET',
                            headers=ContainsKeyValue('X-Auth-Token', TOKEN)).\
            AndReturn((res200, ''))
        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')
