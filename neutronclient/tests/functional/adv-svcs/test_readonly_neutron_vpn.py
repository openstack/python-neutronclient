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

from neutronclient.tests.functional import base


class SimpleReadOnlyNeutronVpnClientTest(base.ClientTestBase):

    """Tests for vpn based client commands that are read only

    This is a first pass at a simple read only python-neutronclient test.
    This only exercises vpn based client commands that are read only.
    This should test commands:
    * as a regular user
    * as a admin user
    * with and without optional parameters
    * initially just check return codes, and later test command outputs
    """
    def setUp(self):
        super(SimpleReadOnlyNeutronVpnClientTest, self).setUp()
        if not self.is_extension_enabled('vpnaas'):
            self.skipTest('VPNaaS is not enabled')

    def test_neutron_vpn_ikepolicy_list(self):
        ikepolicy = self.parser.listing(self.neutron('vpn-ikepolicy-list'))
        self.assertTableStruct(ikepolicy, ['id', 'name',
                                           'auth_algorithm',
                                           'encryption_algorithm',
                                           'ike_version', 'pfs'])

    def test_neutron_vpn_ipsecpolicy_list(self):
        ipsecpolicy = self.parser.listing(self.neutron('vpn-ipsecpolicy-list'))
        self.assertTableStruct(ipsecpolicy, ['id', 'name',
                                             'auth_algorithm',
                                             'encryption_algorithm',
                                             'pfs'])

    def test_neutron_vpn_service_list(self):
        vpn_list = self.parser.listing(self.neutron('vpn-service-list'))
        self.assertTableStruct(vpn_list, ['id', 'name',
                                          'router_id', 'status'])

    def test_neutron_ipsec_site_connection_list(self):
        ipsec_site = self.parser.listing(self.neutron
                                         ('ipsec-site-connection-list'))
        self.assertTableStruct(ipsec_site, ['id', 'name',
                                            'peer_address',
                                            'auth_mode', 'status'])
