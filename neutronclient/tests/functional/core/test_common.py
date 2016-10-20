# Copyright 2016 NEC Corporation
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


class CLICommonFeatureTest(base.ClientTestBase):

    def test_tenant_id_shown_in_list_by_admin(self):
        nets = self.parser.table(self.neutron('net-list'))
        self.assertIn('tenant_id', nets['headers'])

    def test_tenant_id_not_shown_in_list_with_columns(self):
        nets = self.parser.table(self.neutron('net-list -c id -c name'))
        self.assertNotIn('tenant_id', nets['headers'])
        self.assertListEqual(['id', 'name'], nets['headers'])

    def test_tenant_id_not_shown_in_list_by_non_admin(self):
        output = self.neutron_non_admin('net-list')
        self.assertNotIn('tenant_id', self.parser.table(output)['headers'])
        self.assertTableStruct(self.parser.listing(output),
                               ['id', 'name'])
