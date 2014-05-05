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

import json
import uuid

import httpretty
from mox3 import mox
import requests
import testtools

from keystoneclient.auth.identity import v2 as ks_v2_auth
from keystoneclient.auth.identity import v3 as ks_v3_auth
from keystoneclient import exceptions as ks_exceptions
from keystoneclient.fixture import v2 as ks_v2_fixture
from keystoneclient.fixture import v3 as ks_v3_fixture
from keystoneclient import session

from neutronclient import client
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.openstack.common import jsonutils


USERNAME = 'testuser'
USER_ID = 'testuser_id'
TENANT_NAME = 'testtenant'
TENANT_ID = 'testtenant_id'
PASSWORD = 'password'
ENDPOINT_URL = 'localurl'
PUBLIC_ENDPOINT_URL = 'public_%s' % ENDPOINT_URL
ADMIN_ENDPOINT_URL = 'admin_%s' % ENDPOINT_URL
INTERNAL_ENDPOINT_URL = 'internal_%s' % ENDPOINT_URL
ENDPOINT_OVERRIDE = 'otherurl'
TOKEN = 'tokentoken'
TOKENID = uuid.uuid4().hex
REGION = 'RegionOne'
NOAUTH = 'noauth'

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
             'name': 'Neutron Service'}
        ]
    }
}

ENDPOINTS_RESULT = {
    'endpoints': [{
        'type': 'network',
        'name': 'Neutron Service',
        'region': REGION,
        'adminURL': ENDPOINT_URL,
        'internalURL': ENDPOINT_URL,
        'publicURL': ENDPOINT_URL
    }]
}

BASE_HOST = 'http://keystone.example.com'
BASE_URL = "%s:5000/" % BASE_HOST
UPDATED = '2013-03-06T00:00:00Z'

# FIXME (bklei): A future release of keystoneclient will support
# a discovery fixture which can replace these constants and clean
# this up.
V2_URL = "%sv2.0" % BASE_URL
V2_DESCRIBED_BY_HTML = {'href': 'http://docs.openstack.org/api/'
                                'openstack-identity-service/2.0/content/',
                        'rel': 'describedby',
                        'type': 'text/html'}

V2_DESCRIBED_BY_PDF = {'href': 'http://docs.openstack.org/api/openstack-ident'
                               'ity-service/2.0/identity-dev-guide-2.0.pdf',
                       'rel': 'describedby',
                       'type': 'application/pdf'}

V2_VERSION = {'id': 'v2.0',
              'links': [{'href': V2_URL, 'rel': 'self'},
                        V2_DESCRIBED_BY_HTML, V2_DESCRIBED_BY_PDF],
              'status': 'stable',
              'updated': UPDATED}

V3_URL = "%sv3" % BASE_URL
V3_MEDIA_TYPES = [{'base': 'application/json',
                   'type': 'application/vnd.openstack.identity-v3+json'},
                  {'base': 'application/xml',
                   'type': 'application/vnd.openstack.identity-v3+xml'}]

V3_VERSION = {'id': 'v3.0',
              'links': [{'href': V3_URL, 'rel': 'self'}],
              'media-types': V3_MEDIA_TYPES,
              'status': 'stable',
              'updated': UPDATED}


def _create_version_entry(version):
    return jsonutils.dumps({'version': version})


def _create_version_list(versions):
    return jsonutils.dumps({'versions': {'values': versions}})


V3_VERSION_LIST = _create_version_list([V3_VERSION, V2_VERSION])
V3_VERSION_ENTRY = _create_version_entry(V3_VERSION)
V2_VERSION_ENTRY = _create_version_entry(V2_VERSION)


def get_response(status_code, headers=None):
    response = mox.Mox().CreateMock(requests.Response)
    response.headers = headers or {}
    response.status_code = status_code
    return response


def setup_keystone_v2():
    v2_token = ks_v2_fixture.Token(token_id=TOKENID)
    service = v2_token.add_service('network')
    service.add_endpoint(PUBLIC_ENDPOINT_URL, region=REGION)

    httpretty.register_uri(httpretty.POST,
                           '%s/tokens' % (V2_URL),
                           body=json.dumps(v2_token))

    auth_session = session.Session()
    auth_plugin = ks_v2_auth.Password(V2_URL, 'xx', 'xx')
    return auth_session, auth_plugin


def setup_keystone_v3():
    httpretty.register_uri(httpretty.GET,
                           V3_URL,
                           body=V3_VERSION_ENTRY)

    v3_token = ks_v3_fixture.Token()
    service = v3_token.add_service('network')
    service.add_standard_endpoints(public=PUBLIC_ENDPOINT_URL,
                                   admin=ADMIN_ENDPOINT_URL,
                                   internal=INTERNAL_ENDPOINT_URL,
                                   region=REGION)

    httpretty.register_uri(httpretty.POST,
                           '%s/auth/tokens' % (V3_URL),
                           body=json.dumps(v3_token),
                           adding_headers={'X-Subject-Token': TOKENID})

    auth_session = session.Session()
    auth_plugin = ks_v3_auth.Password(V3_URL,
                                      username='xx',
                                      user_id='xx',
                                      user_domain_name='xx',
                                      user_domain_id='xx')
    return auth_session, auth_plugin


AUTH_URL = V2_URL


class CLITestAuthNoAuth(testtools.TestCase):

    def setUp(self):
        """Prepare the test environment."""
        super(CLITestAuthNoAuth, self).setUp()
        self.mox = mox.Mox()
        self.client = client.HTTPClient(username=USERNAME,
                                        tenant_name=TENANT_NAME,
                                        password=PASSWORD,
                                        endpoint_url=ENDPOINT_URL,
                                        auth_strategy=NOAUTH,
                                        region_name=REGION)
        self.addCleanup(self.mox.VerifyAll)
        self.addCleanup(self.mox.UnsetStubs)

    def test_get_noauth(self):
        self.mox.StubOutWithMock(self.client, "request")

        res200 = get_response(200)

        self.client.request(
            mox.StrContains(ENDPOINT_URL + '/resource'), 'GET',
            headers=mox.IsA(dict),
        ).AndReturn((res200, ''))
        self.mox.ReplayAll()

        self.client.do_request('/resource', 'GET')
        self.assertEqual(self.client.endpoint_url, ENDPOINT_URL)


class CLITestAuthKeystone(testtools.TestCase):

    def setUp(self):
        """Prepare the test environment."""
        super(CLITestAuthKeystone, self).setUp()
        self.mox = mox.Mox()

        self.client = client.construct_http_client(
            username=USERNAME,
            tenant_name=TENANT_NAME,
            password=PASSWORD,
            auth_url=AUTH_URL,
            region_name=REGION)

        self.addCleanup(self.mox.VerifyAll)
        self.addCleanup(self.mox.UnsetStubs)

    def test_reused_token_get_auth_info(self):
        """Test that Client.get_auth_info() works even if client was
           instantiated with predefined token.
        """
        client_ = client.HTTPClient(username=USERNAME,
                                    tenant_name=TENANT_NAME,
                                    token=TOKEN,
                                    password=PASSWORD,
                                    auth_url=AUTH_URL,
                                    region_name=REGION)
        expected = {'auth_token': TOKEN,
                    'auth_tenant_id': None,
                    'auth_user_id': None,
                    'endpoint_url': self.client.endpoint_url}
        self.assertEqual(client_.get_auth_info(), expected)

    @httpretty.activate
    def test_get_token(self):
        auth_session, auth_plugin = setup_keystone_v2()

        self.client = client.construct_http_client(
            username=USERNAME,
            tenant_name=TENANT_NAME,
            password=PASSWORD,
            auth_url=AUTH_URL,
            region_name=REGION,
            session=auth_session,
            auth=auth_plugin)

        self.mox.StubOutWithMock(self.client, "request")
        res200 = get_response(200)

        self.client.request(
            '/resource', 'GET',
            authenticated=True
        ).AndReturn((res200, ''))

        self.mox.ReplayAll()

        self.client.do_request('/resource', 'GET')

    def test_refresh_token(self):
        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN
        self.client.endpoint_url = ENDPOINT_URL

        res200 = get_response(200)
        res401 = get_response(401)

        # If a token is expired, neutron server retruns 401
        self.client.request(
            mox.StrContains(ENDPOINT_URL + '/resource'), 'GET',
            headers=mox.ContainsKeyValue('X-Auth-Token', TOKEN)
        ).AndReturn((res401, ''))
        self.client.request(
            AUTH_URL + '/tokens', 'POST',
            body=mox.IsA(str), headers=mox.IsA(dict)
        ).AndReturn((res200, json.dumps(KS_TOKEN_RESULT)))
        self.client.request(
            mox.StrContains(ENDPOINT_URL + '/resource'), 'GET',
            headers=mox.ContainsKeyValue('X-Auth-Token', TOKEN)
        ).AndReturn((res200, ''))
        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')

    def test_refresh_token_no_auth_url(self):
        self.mox.StubOutWithMock(self.client, "request")
        self.client.auth_url = None

        self.client.auth_token = TOKEN
        self.client.endpoint_url = ENDPOINT_URL

        res401 = get_response(401)

        # If a token is expired, neutron server returns 401
        self.client.request(
            mox.StrContains(ENDPOINT_URL + '/resource'), 'GET',
            headers=mox.ContainsKeyValue('X-Auth-Token', TOKEN)
        ).AndReturn((res401, ''))
        self.mox.ReplayAll()
        self.assertRaises(exceptions.NoAuthURLProvided,
                          self.client.do_request,
                          '/resource',
                          'GET')

    def test_get_endpoint_url_with_invalid_auth_url(self):
        # Handle the case when auth_url is not provided
        self.client.auth_url = None
        self.assertRaises(exceptions.NoAuthURLProvided,
                          self.client._get_endpoint_url)

    def test_get_endpoint_url(self):
        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN

        res200 = get_response(200)

        self.client.request(
            mox.StrContains(AUTH_URL + '/tokens/%s/endpoints' % TOKEN), 'GET',
            headers=mox.IsA(dict)
        ).AndReturn((res200, json.dumps(ENDPOINTS_RESULT)))
        self.client.request(
            mox.StrContains(ENDPOINT_URL + '/resource'), 'GET',
            headers=mox.ContainsKeyValue('X-Auth-Token', TOKEN)
        ).AndReturn((res200, ''))
        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')

    def test_use_given_endpoint_url(self):
        self.client = client.HTTPClient(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION,
            endpoint_url=ENDPOINT_OVERRIDE)
        self.assertEqual(self.client.endpoint_url, ENDPOINT_OVERRIDE)

        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN
        res200 = get_response(200)

        self.client.request(
            mox.StrContains(ENDPOINT_OVERRIDE + '/resource'), 'GET',
            headers=mox.ContainsKeyValue('X-Auth-Token', TOKEN)
        ).AndReturn((res200, ''))
        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')
        self.assertEqual(self.client.endpoint_url, ENDPOINT_OVERRIDE)

    def test_get_endpoint_url_other(self):
        self.client = client.HTTPClient(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION, endpoint_type='otherURL')
        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN
        res200 = get_response(200)

        self.client.request(
            mox.StrContains(AUTH_URL + '/tokens/%s/endpoints' % TOKEN), 'GET',
            headers=mox.IsA(dict)
        ).AndReturn((res200, json.dumps(ENDPOINTS_RESULT)))
        self.mox.ReplayAll()
        self.assertRaises(exceptions.EndpointTypeNotFound,
                          self.client.do_request,
                          '/resource',
                          'GET')

    def test_get_endpoint_url_failed(self):
        self.mox.StubOutWithMock(self.client, "request")

        self.client.auth_token = TOKEN

        res200 = get_response(200)
        res401 = get_response(401)

        self.client.request(
            mox.StrContains(AUTH_URL + '/tokens/%s/endpoints' % TOKEN), 'GET',
            headers=mox.IsA(dict)
        ).AndReturn((res401, ''))
        self.client.request(
            AUTH_URL + '/tokens', 'POST',
            body=mox.IsA(str), headers=mox.IsA(dict)
        ).AndReturn((res200, json.dumps(KS_TOKEN_RESULT)))
        self.client.request(
            mox.StrContains(ENDPOINT_URL + '/resource'), 'GET',
            headers=mox.ContainsKeyValue('X-Auth-Token', TOKEN)
        ).AndReturn((res200, ''))
        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')

    @httpretty.activate
    def test_endpoint_type(self):
        auth_session, auth_plugin = setup_keystone_v3()

        # Test default behavior is to choose public.
        self.client = client.construct_http_client(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION,
            session=auth_session, auth=auth_plugin)

        self.client.authenticate()
        self.assertEqual(self.client.endpoint_url, PUBLIC_ENDPOINT_URL)

        # Test admin url
        self.client = client.construct_http_client(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION, endpoint_type='adminURL',
            session=auth_session, auth=auth_plugin)

        self.client.authenticate()
        self.assertEqual(self.client.endpoint_url, ADMIN_ENDPOINT_URL)

        # Test public url
        self.client = client.construct_http_client(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION, endpoint_type='publicURL',
            session=auth_session, auth=auth_plugin)

        self.client.authenticate()
        self.assertEqual(self.client.endpoint_url, PUBLIC_ENDPOINT_URL)

        # Test internal url
        self.client = client.construct_http_client(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION, endpoint_type='internalURL',
            session=auth_session, auth=auth_plugin)

        self.client.authenticate()
        self.assertEqual(self.client.endpoint_url, INTERNAL_ENDPOINT_URL)

        # Test url that isn't found in the service catalog
        self.client = client.construct_http_client(
            username=USERNAME, tenant_name=TENANT_NAME, password=PASSWORD,
            auth_url=AUTH_URL, region_name=REGION, endpoint_type='privateURL',
            session=auth_session, auth=auth_plugin)

        self.assertRaises(
            ks_exceptions.EndpointNotFound,
            self.client.authenticate)

    def test_strip_credentials_from_log(self):
        def verify_no_credentials(kwargs):
            return ('REDACTED' in kwargs['body']) and (
                self.client.password not in kwargs['body'])

        def verify_credentials(body):
            return 'REDACTED' not in body and self.client.password in body

        self.mox.StubOutWithMock(self.client, "request")
        self.mox.StubOutWithMock(utils, "http_log_req")

        res200 = get_response(200)

        utils.http_log_req(mox.IgnoreArg(), mox.IgnoreArg(), mox.Func(
            verify_no_credentials))
        self.client.request(
            mox.IsA(str), mox.IsA(str), body=mox.Func(verify_credentials),
            headers=mox.IgnoreArg()
        ).AndReturn((res200, json.dumps(KS_TOKEN_RESULT)))
        utils.http_log_req(mox.IgnoreArg(), mox.IgnoreArg(), mox.IgnoreArg())
        self.client.request(
            mox.IsA(str), mox.IsA(str), headers=mox.IsA(dict)
        ).AndReturn((res200, ''))
        self.mox.ReplayAll()

        self.client.do_request('/resource', 'GET')


class CLITestAuthKeystoneWithId(CLITestAuthKeystone):

    def setUp(self):
        """Prepare the test environment."""
        super(CLITestAuthKeystoneWithId, self).setUp()
        self.client = client.HTTPClient(user_id=USER_ID,
                                        tenant_id=TENANT_ID,
                                        password=PASSWORD,
                                        auth_url=AUTH_URL,
                                        region_name=REGION)


class CLITestAuthKeystoneWithIdandName(CLITestAuthKeystone):

    def setUp(self):
        """Prepare the test environment."""
        super(CLITestAuthKeystoneWithIdandName, self).setUp()
        self.client = client.HTTPClient(username=USERNAME,
                                        user_id=USER_ID,
                                        tenant_id=TENANT_ID,
                                        tenant_name=TENANT_NAME,
                                        password=PASSWORD,
                                        auth_url=AUTH_URL,
                                        region_name=REGION)


class TestKeystoneClientVersions(testtools.TestCase):

    def setUp(self):
        """Prepare the test environment."""
        super(TestKeystoneClientVersions, self).setUp()
        self.mox = mox.Mox()
        self.addCleanup(self.mox.VerifyAll)
        self.addCleanup(self.mox.UnsetStubs)

    @httpretty.activate
    def test_v2_auth(self):
        auth_session, auth_plugin = setup_keystone_v2()
        res200 = get_response(200)

        self.client = client.construct_http_client(
            username=USERNAME,
            tenant_name=TENANT_NAME,
            password=PASSWORD,
            auth_url=AUTH_URL,
            region_name=REGION,
            session=auth_session,
            auth=auth_plugin)

        self.mox.StubOutWithMock(self.client, "request")

        self.client.request(
            '/resource', 'GET',
            authenticated=True
        ).AndReturn((res200, ''))

        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')

    @httpretty.activate
    def test_v3_auth(self):
        auth_session, auth_plugin = setup_keystone_v3()
        res200 = get_response(200)

        self.client = client.construct_http_client(
            user_id=USER_ID,
            tenant_id=TENANT_ID,
            password=PASSWORD,
            auth_url=V3_URL,
            region_name=REGION,
            session=auth_session,
            auth=auth_plugin)

        self.mox.StubOutWithMock(self.client, "request")

        self.client.request(
            '/resource', 'GET',
            authenticated=True
        ).AndReturn((res200, ''))

        self.mox.ReplayAll()
        self.client.do_request('/resource', 'GET')
