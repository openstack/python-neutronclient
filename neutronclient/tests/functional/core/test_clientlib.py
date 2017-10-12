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

from keystoneauth1 import session
from oslo_utils import uuidutils
from tempest.lib import base
import testtools

from neutronclient.common import exceptions
from neutronclient.tests.functional import base as func_base
from neutronclient.v2_0 import client as v2_client


class LibraryTestCase(base.BaseTestCase):

    def setUp(self):
        super(LibraryTestCase, self).setUp()
        self.client = self._get_client()

    def _get_client(self):
        cloud_config = func_base.get_cloud_config()
        keystone_auth = cloud_config.get_auth()
        (verify, cert) = cloud_config.get_requests_verify_args()

        ks_session = session.Session(
            auth=keystone_auth,
            verify=verify,
            cert=cert)
        return v2_client.Client(session=ks_session)

    def test_list_network(self):
        nets = self.client.list_networks()
        self.assertIsInstance(nets['networks'], list)

    def test_post_put_delete_network(self):
        name = uuidutils.generate_uuid()
        net = self.client.create_network({'network': {'name': name}})
        net_id = net['network']['id']
        self.assertEqual(name, net['network']['name'])
        name2 = uuidutils.generate_uuid()
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
