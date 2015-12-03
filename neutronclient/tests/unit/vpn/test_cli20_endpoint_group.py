#    (c) Copyright 2015 Cisco Systems, Inc.
#    All Rights Reserved.
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

import sys

from neutronclient.neutron.v2_0.vpn import endpoint_group
from neutronclient.tests.unit import test_cli20


class CLITestV20VpnEndpointGroupJSON(test_cli20.CLITestV20Base):

    def setUp(self):
        super(CLITestV20VpnEndpointGroupJSON, self).setUp()
        self.register_non_admin_status_resource('endpoint_group')

    def test_create_endpoint_group_with_cidrs(self):
        # vpn-endpoint-group-create with CIDR endpoints."""
        resource = 'endpoint_group'
        cmd = endpoint_group.CreateEndpointGroup(test_cli20.MyApp(sys.stdout),
                                                 None)
        tenant_id = 'mytenant-id'
        my_id = 'my-id'
        name = 'my-endpoint-group'
        description = 'my endpoint group'
        endpoint_type = 'cidr'
        endpoints = ['10.0.0.0/24', '20.0.0.0/24']

        args = ['--name', name,
                '--description', description,
                '--tenant-id', tenant_id,
                '--type', endpoint_type,
                '--value', '10.0.0.0/24',
                '--value', '20.0.0.0/24']

        position_names = ['name', 'description', 'tenant_id',
                          'type', 'endpoints']

        position_values = [name, description, tenant_id,
                           endpoint_type, endpoints]

        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values)

    def test_create_endpoint_group_with_subnets(self):
        # vpn-endpoint-group-create with subnet endpoints."""
        resource = 'endpoint_group'
        cmd = endpoint_group.CreateEndpointGroup(test_cli20.MyApp(sys.stdout),
                                                 None)
        tenant_id = 'mytenant-id'
        my_id = 'my-id'
        endpoint_type = 'subnet'
        subnet = 'subnet-id'
        endpoints = [subnet]

        args = ['--type', endpoint_type,
                '--value', subnet,
                '--tenant-id', tenant_id]

        position_names = ['type', 'endpoints', 'tenant_id']

        position_values = [endpoint_type, endpoints, tenant_id]

        self._test_create_resource(resource, cmd, None, my_id, args,
                                   position_names, position_values)

    def test_list_endpoint_group(self):
        # vpn-endpoint-group-list.
        resources = "endpoint_groups"
        cmd = endpoint_group.ListEndpointGroup(test_cli20.MyApp(sys.stdout),
                                               None)
        self._test_list_resources(resources, cmd, True)

    def test_list_endpoint_group_pagination(self):
        # vpn-endpoint-group-list.
        resources = "endpoint_groups"
        cmd = endpoint_group.ListEndpointGroup(test_cli20.MyApp(sys.stdout),
                                               None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_endpoint_group_sort(self):
        # vpn-endpoint-group-list --sort-key name --sort-key id
        # --sort-key asc --sort-key desc
        resources = "endpoint_groups"
        cmd = endpoint_group.ListEndpointGroup(test_cli20.MyApp(sys.stdout),
                                               None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_endpoint_group_limit(self):
        # vpn-endpoint-group-list -P.
        resources = "endpoint_groups"
        cmd = endpoint_group.ListEndpointGroup(test_cli20.MyApp(sys.stdout),
                                               None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_show_endpoint_group_id(self):
        # vpn-endpoint-group-show test_id.
        resource = 'endpoint_group'
        cmd = endpoint_group.ShowEndpointGroup(test_cli20.MyApp(sys.stdout),
                                               None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'])

    def test_show_endpoint_group_id_name(self):
        # vpn-endpoint-group-show.
        resource = 'endpoint_group'
        cmd = endpoint_group.ShowEndpointGroup(test_cli20.MyApp(sys.stdout),
                                               None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_update_endpoint_group(self):
        # vpn-endpoint-group-update myid --name newname --description newdesc.
        resource = 'endpoint_group'
        cmd = endpoint_group.UpdateEndpointGroup(test_cli20.MyApp(sys.stdout),
                                                 None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'newname',
                                    '--description', 'newdesc'],
                                   {'name': 'newname',
                                    'description': 'newdesc'})

    def test_delete_endpoint_group(self):
        # vpn-endpoint-group-delete my-id.
        resource = 'endpoint_group'
        cmd = endpoint_group.DeleteEndpointGroup(test_cli20.MyApp(sys.stdout),
                                                 None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)
