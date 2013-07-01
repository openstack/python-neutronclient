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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import fixtures
import httplib2
import mox
import testtools

from neutronclient.client import HTTPClient
from neutronclient.common.clientmanager import ClientManager
from neutronclient.common import exceptions
from neutronclient import shell as openstack_shell


AUTH_TOKEN = 'test_token'
END_URL = 'test_url'
METHOD = 'GET'
URL = 'http://test.test:1234/v2.0/'
CA_CERT = '/tmp/test/path'


class TestSSL(testtools.TestCase):
    def setUp(self):
        super(TestSSL, self).setUp()

        self.useFixture(fixtures.EnvironmentVariable('OS_TOKEN', AUTH_TOKEN))
        self.useFixture(fixtures.EnvironmentVariable('OS_URL', END_URL))

        self.mox = mox.Mox()
        self.addCleanup(self.mox.UnsetStubs)

    def test_ca_cert_passed(self):
        self.mox.StubOutWithMock(ClientManager, '__init__')
        self.mox.StubOutWithMock(openstack_shell.NeutronShell, 'interact')

        ClientManager.__init__(
            ca_cert=CA_CERT,
            # we are not really interested in other args
            api_version=mox.IgnoreArg(),
            auth_strategy=mox.IgnoreArg(),
            auth_url=mox.IgnoreArg(),
            endpoint_type=mox.IgnoreArg(),
            insecure=mox.IgnoreArg(),
            password=mox.IgnoreArg(),
            region_name=mox.IgnoreArg(),
            tenant_id=mox.IgnoreArg(),
            tenant_name=mox.IgnoreArg(),
            token=mox.IgnoreArg(),
            url=mox.IgnoreArg(),
            username=mox.IgnoreArg(),
            log_credentials=mox.IgnoreArg(),
        )
        openstack_shell.NeutronShell.interact().AndReturn(0)
        self.mox.ReplayAll()

        openstack_shell.NeutronShell('2.0').run(['--os-cacert', CA_CERT])
        self.mox.VerifyAll()

    def test_ca_cert_passed_as_env_var(self):
        self.useFixture(fixtures.EnvironmentVariable('OS_CACERT', CA_CERT))

        self.mox.StubOutWithMock(ClientManager, '__init__')
        self.mox.StubOutWithMock(openstack_shell.NeutronShell, 'interact')

        ClientManager.__init__(
            ca_cert=CA_CERT,
            # we are not really interested in other args
            api_version=mox.IgnoreArg(),
            auth_strategy=mox.IgnoreArg(),
            auth_url=mox.IgnoreArg(),
            endpoint_type=mox.IgnoreArg(),
            insecure=mox.IgnoreArg(),
            password=mox.IgnoreArg(),
            region_name=mox.IgnoreArg(),
            tenant_id=mox.IgnoreArg(),
            tenant_name=mox.IgnoreArg(),
            token=mox.IgnoreArg(),
            url=mox.IgnoreArg(),
            username=mox.IgnoreArg(),
            log_credentials=mox.IgnoreArg(),
        )
        openstack_shell.NeutronShell.interact().AndReturn(0)
        self.mox.ReplayAll()

        openstack_shell.NeutronShell('2.0').run([])
        self.mox.VerifyAll()

    def test_client_manager_properly_creates_httpclient_instance(self):
        self.mox.StubOutWithMock(HTTPClient, '__init__')
        HTTPClient.__init__(
            ca_cert=CA_CERT,
            # we are not really interested in other args
            auth_strategy=mox.IgnoreArg(),
            auth_url=mox.IgnoreArg(),
            endpoint_url=mox.IgnoreArg(),
            insecure=mox.IgnoreArg(),
            password=mox.IgnoreArg(),
            region_name=mox.IgnoreArg(),
            tenant_name=mox.IgnoreArg(),
            token=mox.IgnoreArg(),
            username=mox.IgnoreArg(),
        )
        self.mox.ReplayAll()

        version = {'network': '2.0'}
        ClientManager(ca_cert=CA_CERT,
                      api_version=version,
                      url=END_URL,
                      token=AUTH_TOKEN).neutron
        self.mox.VerifyAll()

    def test_proper_exception_is_raised_when_cert_validation_fails(self):
        http = HTTPClient(token=AUTH_TOKEN, endpoint_url=END_URL)

        self.mox.StubOutWithMock(httplib2.Http, 'request')
        httplib2.Http.request(
            URL, METHOD, headers=mox.IgnoreArg()
        ).AndRaise(httplib2.SSLHandshakeError)
        self.mox.ReplayAll()

        self.assertRaises(
            exceptions.SslCertificateValidationError,
            http._cs_request,
            URL, METHOD
        )
        self.mox.VerifyAll()
