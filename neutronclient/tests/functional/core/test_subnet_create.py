# Copyright 2015 Hewlett-Packard Development Company, L.P
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutronclient.tests.functional import base


class SubnetCreateNeutronClientCLITest(base.ClientTestBase):

    def test_create_subnet_net_name_first(self):
        self.neutron('net-create', params='netwrk-1')
        self.addCleanup(self.neutron, 'net-delete netwrk-1')
        self.neutron('subnet-create netwrk-1',
                     params='--name fake --gateway 192.168.51.1 '
                            '192.168.51.0/24')
        self.addCleanup(self.neutron, 'subnet-delete fake')
        subnet_list = self.parser.listing(self.neutron('subnet-list'))
        self.assertTableStruct(subnet_list, ['id', 'name', 'cidr',
                                             'allocation_pools'])
        found = False
        for row in subnet_list:
            if row.get('name') == 'fake':
                found = True
                break
        if not found:
            self.fail('Created subnet not found in list')
