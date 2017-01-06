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

import uuid

from keystoneauth1 import plugin as ksa_plugin
from keystoneauth1 import session
from tempest.lib import base
import testtools

from neutronclient.common import exceptions
from neutronclient.tests.functional import base as func_base
from neutronclient.v2_0 import client as v2_client

# This module tests client library functionalities with
# Keystone client. Neutron client supports two types of
# HTTP clients (HTTPClient and SessionClient),
# so it is better to test both clients.


class LibraryTestBase(base.BaseTestCase):

    def setUp(self):
        super(LibraryTestBase, self).setUp()
        self.client = self._get_client()


class Libv2HTTPClientTestBase(LibraryTestBase):

    def _setup_creds(self):
        creds = func_base.credentials()
        cloud_config = func_base.get_cloud_config()

        # We're getting a session so we can find the v2 url via KSA
        keystone_auth = cloud_config.get_auth()
        (verify, cert) = cloud_config.get_requests_verify_args()

        ks_session = session.Session(
            auth=keystone_auth, verify=verify, cert=cert)

        # for the old HTTPClient, we use keystone v2 API, regardless of
        # whether v3 also exists or is configured
        v2_auth_url = keystone_auth.get_endpoint(
            ks_session, interface=ksa_plugin.AUTH_INTERFACE, version=(2, 0))
        return v2_auth_url, creds


class Libv2HTTPClientTenantTestBase(Libv2HTTPClientTestBase):

    def _get_client(self):
        v2_auth_url, creds = self._setup_creds()
        return v2_client.Client(username=creds['username'],
                                password=creds['password'],
                                tenant_name=creds['project_name'],
                                auth_url=v2_auth_url)


class Libv2HTTPClientProjectTestBase(Libv2HTTPClientTestBase):

    def _get_client(self):
        v2_auth_url, creds = self._setup_creds()
        return v2_client.Client(username=creds['username'],
                                password=creds['password'],
                                project_name=creds['project_name'],
                                auth_url=v2_auth_url)


class Libv2SessionClientTestBase(LibraryTestBase):

    def _get_client(self):
        cloud_config = func_base.get_cloud_config()
        keystone_auth = cloud_config.get_auth()
        (verify, cert) = cloud_config.get_requests_verify_args()

        ks_session = session.Session(
            auth=keystone_auth,
            verify=verify,
            cert=cert)
        return v2_client.Client(session=ks_session)


class LibraryTestCase(object):

    def test_list_network(self):
        nets = self.client.list_networks()
        self.assertIsInstance(nets['networks'], list)

    def test_post_put_delete_network(self):
        name = str(uuid.uuid4())
        net = self.client.create_network({'network': {'name': name}})
        net_id = net['network']['id']
        self.assertEqual(name, net['network']['name'])
        name2 = str(uuid.uuid4())
        net = self.client.update_network(net_id, {'network': {'name': name2}})
        self.assertEqual(name2, net['network']['name'])
        self.client.delete_network(net_id)
        with testtools.ExpectedException(exceptions.NetworkNotFoundClient):
            self.client.show_network(net_id)

    def test_get_auth_ref(self):
        # Call some API call to ensure the client is authenticated.
        self.client.list_networks()
        auth_ref = self.client.httpclient.get_auth_ref()
        self.assertIsNotNone(auth_ref)
        self.assertIsNotNone(auth_ref.role_names)


class LibraryHTTPClientTenantTest(LibraryTestCase,
                                  Libv2HTTPClientTenantTestBase):
    pass


class LibraryHTTPClientProjectTest(LibraryTestCase,
                                   Libv2HTTPClientProjectTestBase):
    pass


class LibrarySessionClientTest(LibraryTestCase, Libv2SessionClientTestBase):
    pass
