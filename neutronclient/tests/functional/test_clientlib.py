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

import os
import uuid

from keystoneclient.auth.identity import v2 as v2_auth
from keystoneclient import discover
from keystoneclient import session
from tempest_lib import base
import testtools

from neutronclient.common import exceptions
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

    def _get_client(self):
        return v2_client.Client(username=os.environ.get('OS_USERNAME'),
                                password=os.environ.get('OS_PASSWORD'),
                                tenant_name=os.environ.get('OS_TENANT_NAME'),
                                auth_url=os.environ.get('OS_AUTH_URL'))


class Libv2SessionClientTestBase(LibraryTestBase):

    def _get_client(self):
        session_params = {}
        ks_session = session.Session.construct(session_params)
        ks_discover = discover.Discover(session=ks_session,
                                        auth_url=os.environ.get('OS_AUTH_URL'))
        # At the moment, we use keystone v2 API
        v2_auth_url = ks_discover.url_for('2.0')
        ks_session.auth = v2_auth.Password(
            v2_auth_url,
            username=os.environ.get('OS_USERNAME'),
            password=os.environ.get('OS_PASSWORD'),
            tenant_name=os.environ.get('OS_TENANT_NAME'))
        return v2_client.Client(session=ks_session)


class LibraryTestCase(object):

    def test_list_network(self):
        nets = self.client.list_networks()
        self.assertIsInstance(nets['networks'], list)

    def test_post_put_delele_network(self):
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


class LibraryHTTPClientTest(LibraryTestCase, Libv2HTTPClientTestBase):
    pass


class LibrarySessionClientTest(LibraryTestCase, Libv2SessionClientTestBase):
    pass
