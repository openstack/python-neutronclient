# Copyright 2015 OpenStack Foundation.
# All Rights Reserved
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

import mock

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0 import subnetpool
from neutronclient.tests.unit import test_cli20


class CLITestV20SubnetPoolJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['subnetpool']

    def setUp(self):
        super(CLITestV20SubnetPoolJSON, self).setUp(plurals={'tags': 'tag'})

    def test_create_subnetpool_with_options(self):
        # Create subnetpool: myname.
        resource = 'subnetpool'
        cmd = subnetpool.CreateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        min_prefixlen = 30
        prefix1 = '10.11.12.0/24'
        prefix2 = '12.11.13.0/24'
        args = [name, '--min-prefixlen', str(min_prefixlen),
                '--pool-prefix', prefix1, '--pool-prefix', prefix2,
                '--shared', '--description', 'public pool',
                '--tenant-id', 'tenantid']
        position_names = ['name', 'min_prefixlen', 'prefixes', 'shared',
                          'tenant_id']
        position_values = [name, min_prefixlen, [prefix1, prefix2], True,
                           'tenantid']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   description='public pool')

    def test_create_subnetpool_only_with_required_options(self):
        # Create subnetpool: myname.
        resource = 'subnetpool'
        cmd = subnetpool.CreateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        min_prefixlen = 30
        prefix1 = '10.11.12.0/24'
        prefix2 = '12.11.13.0/24'
        args = [name, '--min-prefixlen', str(min_prefixlen),
                '--pool-prefix', prefix1, '--pool-prefix', prefix2]
        position_names = ['name', 'min_prefixlen', 'prefixes']
        position_values = [name, min_prefixlen, [prefix1, prefix2]]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_subnetpool_with_is_default(self, default='false'):
        # Create subnetpool: myname.
        resource = 'subnetpool'
        cmd = subnetpool.CreateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        min_prefixlen = 30
        prefix1 = '10.11.12.0/24'
        prefix2 = '12.11.13.0/24'
        args = [name, '--min-prefixlen', str(min_prefixlen),
                '--pool-prefix', prefix1, '--pool-prefix', prefix2,
                '--is-default', default]
        position_names = ['name', 'min_prefixlen', 'prefixes', 'is_default']
        position_values = [name, min_prefixlen, [prefix1, prefix2], default]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_subnetpool_default(self):
        self.test_create_subnetpool_with_is_default(default='true')

    def test_create_subnetpool_with_unicode(self):
        # Create subnetpool: u'\u7f51\u7edc'.
        resource = 'subnetpool'
        cmd = subnetpool.CreateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        name = u'\u7f51\u7edc'
        myid = 'myid'
        min_prefixlen = 30
        prefixes = '10.11.12.0/24'
        args = [name, '--min-prefixlen', str(min_prefixlen),
                '--pool-prefix', prefixes]
        position_names = ['name', 'min_prefixlen', 'prefixes']
        position_values = [name, min_prefixlen, [prefixes]]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_subnetpool_with_addrscope(self):
        # Create subnetpool: myname in addrscope: foo-address-scope
        resource = 'subnetpool'
        cmd = subnetpool.CreateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        min_prefixlen = 30
        prefix1 = '11.11.11.0/24'
        prefix2 = '12.12.12.0/24'
        address_scope = 'foo-address-scope'
        args = [name, '--min-prefixlen', str(min_prefixlen),
                '--pool-prefix', prefix1, '--pool-prefix', prefix2,
                '--address-scope', address_scope]
        position_names = ['name', 'min_prefixlen', 'prefixes',
                          'address_scope_id']
        position_values = [name, min_prefixlen, [prefix1, prefix2],
                           address_scope]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_subnetpool_no_poolprefix(self):
        # Should raise an error because --pool-prefix is required
        resource = 'subnetpool'
        cmd = subnetpool.CreateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self.assertRaises(SystemExit, self._test_create_resource, resource,
                          cmd, name, myid, args, position_names,
                          position_values)

    @mock.patch.object(subnetpool.ListSubnetPool, "extend_list")
    def test_list_subnetpool_pagination(self, mock_extend_list):
        cmd = subnetpool.ListSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination("subnetpools", cmd)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def test_list_subnetpools_sort(self):
        # List subnetpools:
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "subnetpools"
        cmd = subnetpool.ListSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_subnetpools_limit(self):
        # List subnetpools: -P.
        resources = "subnetpools"
        cmd = subnetpool.ListSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_update_subnetpool_exception(self):
        # Update subnetpool: myid.
        resource = 'subnetpool'
        cmd = subnetpool.UpdateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_update_subnetpool(self):
        # Update subnetpool: myid --name myname.
        resource = 'subnetpool'
        cmd = subnetpool.UpdateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--description', ':)'],
                                   {'name': 'myname', 'description': ':)'})

    def test_update_subnetpool_with_address_scope(self):
        # Update subnetpool: myid --address-scope newscope.
        resource = 'subnetpool'
        cmd = subnetpool.UpdateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--address-scope', 'newscope'],
                                   {'address_scope_id': 'newscope'}
                                   )

    def test_update_subnetpool_with_no_address_scope(self):
        # Update subnetpool: myid --no-address-scope.
        resource = 'subnetpool'
        cmd = subnetpool.UpdateSubnetPool(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--no-address-scope'],
                                   {'address_scope_id': None}
                                   )

    def test_show_subnetpool(self):
        # Show subnetpool: --fields id --fields name myid.
        resource = 'subnetpool'
        cmd = subnetpool.ShowSubnetPool(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_delete_subnetpool(self):
        # Delete subnetpool: subnetpoolid.
        resource = 'subnetpool'
        cmd = subnetpool.DeleteSubnetPool(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
