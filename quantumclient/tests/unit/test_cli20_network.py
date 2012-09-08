# Copyright 2012 OpenStack LLC.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient.tests.unit import test_cli20
from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp
from quantumclient.quantum.v2_0.network import CreateNetwork
from quantumclient.quantum.v2_0.network import ListNetwork
from quantumclient.quantum.v2_0.network import UpdateNetwork
from quantumclient.quantum.v2_0.network import ShowNetwork
from quantumclient.quantum.v2_0.network import DeleteNetwork


class CLITestV20Network(CLITestV20Base):
    def test_create_network(self):
        """Create net: myname."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_network_tenant(self):
        """Create net: --tenant_id tenantid myname."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--tenant_id', 'tenantid', name]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

        # Test dashed options
        args = ['--tenant-id', 'tenantid', name]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_network_tags(self):
        """Create net: myname --tags a b."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name, '--tags', 'a', 'b']
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tags=['a', 'b'])

    def test_create_network_state(self):
        """Create net: --admin_state_down myname."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--admin_state_down', name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          admin_state_up=False)

        # Test dashed options
        args = ['--admin-state-down', name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          admin_state_up=False)

    def test_list_nets_empty_with_column(self):
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        reses = {resources: []}
        resstr = self.client.serialize(reses)
        # url method body
        query = "id=myfakeid"
        args = ['-c', 'id', '--', '--id', 'myfakeid']
        path = getattr(self.client, resources + "_path")
        self.client.httpclient.request(
            test_cli20.end_url(path, query), 'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                'X-Auth-Token',
                test_cli20.TOKEN)).AndReturn(
                    (test_cli20.MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)

        parsed_args = cmd_parser.parse_args(args)
        cmd.run(parsed_args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertEquals('\n', _str)

    def test_list_nets_detail(self):
        """list nets: -D."""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_nets_tags(self):
        """List nets: -- --tags a b."""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_nets_detail_tags(self):
        """List nets: -D -- --tags a b."""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_nets_fields(self):
        """List nets: --fields a --fields b -- --fields c d."""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def test_list_nets_defined_column(self):
        resources = 'networks'
        cmd = ListNetwork(MyApp(sys.stdout), None)
        returned_body = {"networks": [{"name": "buildname3",
                                       "id": "id3",
                                       "tenant_id": "tenant_3",
                                       "subnets": []}]}
        self._test_list_columns(cmd, resources, returned_body,
                                args=['-f', 'json', '-c', 'id'])
        _str = self.fake_stdout.make_string()
        returned_networks = utils.loads(_str)
        self.assertEquals(1, len(returned_networks))
        network = returned_networks[0]
        self.assertEquals(1, len(network))
        self.assertEquals("id", network.keys()[0])

    def test_list_nets_with_default_column(self):
        resources = 'networks'
        cmd = ListNetwork(MyApp(sys.stdout), None)
        returned_body = {"networks": [{"name": "buildname3",
                                       "id": "id3",
                                       "tenant_id": "tenant_3",
                                       "subnets": []}]}
        self._test_list_columns(cmd, resources, returned_body)
        _str = self.fake_stdout.make_string()
        returned_networks = utils.loads(_str)
        self.assertEquals(1, len(returned_networks))
        network = returned_networks[0]
        self.assertEquals(3, len(network))
        self.assertEquals(0, len(set(network) ^
                                 set(cmd.list_columns)))

    def test_update_network_exception(self):
        """Update net: myid."""
        resource = 'network'
        cmd = UpdateNetwork(MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_update_network(self):
        """Update net: myid --name myname --tags a b."""
        resource = 'network'
        cmd = UpdateNetwork(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_show_network(self):
        """Show net: --fields id --fields name myid."""
        resource = 'network'
        cmd = ShowNetwork(MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_delete_network(self):
        """Delete net: myid."""
        resource = 'network'
        cmd = DeleteNetwork(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
