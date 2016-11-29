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


class SimpleReadOnlyNeutronFwv1ClientTest(base.ClientTestBase):

    """Tests for FWaaS v1 based client commands that are read only"""

    def setUp(self):
        super(SimpleReadOnlyNeutronFwv1ClientTest, self).setUp()
        if not self.is_extension_enabled('fwaas'):
            self.skipTest('FWaaS is not enabled')

    def test_neutron_firewall_list(self):
        firewall_list = self.parser.listing(self.neutron
                                            ('firewall-list'))
        self.assertTableStruct(firewall_list, ['id', 'name',
                                               'firewall_policy_id'])

    def test_neutron_firewall_policy_list(self):
        firewall_policy = self.parser.listing(self.neutron
                                              ('firewall-policy-list'))
        self.assertTableStruct(firewall_policy, ['id', 'name',
                                                 'firewall_rules'])

    def test_neutron_firewall_rule_list(self):
        firewall_rule = self.parser.listing(self.neutron
                                            ('firewall-rule-list'))
        self.assertTableStruct(firewall_rule, ['id', 'name',
                                               'firewall_policy_id',
                                               'summary', 'enabled'])
