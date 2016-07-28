# Copyright 2016 NEC Corporation
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

import testtools

from neutronclient.osc import utils


class TestUtils(testtools.TestCase):

    def test_get_column_definitions(self):
        attr_map = (
            ('id', 'ID', utils.LIST_BOTH),
            ('tenant_id', 'Project', utils.LIST_LONG_ONLY),
            ('name', 'Name', utils.LIST_BOTH),
            ('summary', 'Summary', utils.LIST_SHORT_ONLY),
        )
        headers, columns = utils.get_column_definitions(attr_map,
                                                        long_listing=False)
        self.assertEqual(['id', 'name', 'summary'], columns)
        self.assertEqual(['ID', 'Name', 'Summary'], headers)

    def test_get_column_definitions_long(self):
        attr_map = (
            ('id', 'ID', utils.LIST_BOTH),
            ('tenant_id', 'Project', utils.LIST_LONG_ONLY),
            ('name', 'Name', utils.LIST_BOTH),
            ('summary', 'Summary', utils.LIST_SHORT_ONLY),
        )
        headers, columns = utils.get_column_definitions(attr_map,
                                                        long_listing=True)
        self.assertEqual(['id', 'tenant_id', 'name'], columns)
        self.assertEqual(['ID', 'Project', 'Name'], headers)

    def test_get_columns(self):
        item = {
            'id': 'test-id',
            'tenant_id': 'test-tenant_id',
            # 'name' is not included
            'foo': 'bar',  # unknown attribute
        }
        attr_map = (
            ('id', 'ID', utils.LIST_BOTH),
            ('tenant_id', 'Project', utils.LIST_LONG_ONLY),
            ('name', 'Name', utils.LIST_BOTH),
        )
        columns, display_names = utils.get_columns(item, attr_map)
        self.assertEqual(tuple(['id', 'tenant_id', 'foo']), columns)
        self.assertEqual(tuple(['ID', 'Project', 'foo']), display_names)
