# Copyright 2012 Nicira, Inc
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
from quantumclient.quantum.v2_0.router import AddInterfaceRouter
from quantumclient.quantum.v2_0.router import CreateRouter
from quantumclient.quantum.v2_0.router import DeleteRouter
from quantumclient.quantum.v2_0.router import ListRouter
from quantumclient.quantum.v2_0.router import RemoveGatewayRouter
from quantumclient.quantum.v2_0.router import RemoveInterfaceRouter
from quantumclient.quantum.v2_0.router import SetGatewayRouter
from quantumclient.quantum.v2_0.router import ShowRouter
from quantumclient.quantum.v2_0.router import UpdateRouter
from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp


class CLITestV20Router(CLITestV20Base):
    def test_create_router(self):
        """Create router: router1."""
        resource = 'router'
        cmd = CreateRouter(MyApp(sys.stdout), None)
        name = 'router1'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_router_tenant(self):
        """Create router: --tenant_id tenantid myname."""
        resource = 'router'
        cmd = CreateRouter(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--tenant_id', 'tenantid', name]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_router_admin_state(self):
        """Create router: --admin_state_down myname."""
        resource = 'router'
        cmd = CreateRouter(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--admin_state_down', name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          admin_state_up=False)

    def test_list_routers_detail(self):
        """list routers: -D."""
        resources = "routers"
        cmd = ListRouter(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_update_router_exception(self):
        """Update router: myid."""
        resource = 'router'
        cmd = UpdateRouter(MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_update_router(self):
        """Update router: myid --name myname --tags a b."""
        resource = 'router'
        cmd = UpdateRouter(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname'],
                                   {'name': 'myname'}
                                   )

    def test_delete_router(self):
        """Delete router: myid."""
        resource = 'router'
        cmd = DeleteRouter(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_show_router(self):
        """Show router: myid."""
        resource = 'router'
        cmd = ShowRouter(MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_add_interface(self):
        """Add interface to router: myid subnetid"""
        resource = 'router'
        cmd = AddInterfaceRouter(MyApp(sys.stdout), None)
        args = ['myid', 'subnetid']
        self._test_update_resource_action(resource, cmd, 'myid',
                                          'add_router_interface',
                                          args,
                                          {'subnet_id': 'subnetid'}
                                          )

    def test_del_interface(self):
        """Delete interface from router: myid subnetid"""
        resource = 'router'
        cmd = RemoveInterfaceRouter(MyApp(sys.stdout), None)
        args = ['myid', 'subnetid']
        self._test_update_resource_action(resource, cmd, 'myid',
                                          'remove_router_interface',
                                          args,
                                          {'subnet_id': 'subnetid'}
                                          )

    def test_set_gateway(self):
        """Set external gateway for router: myid externalid"""
        resource = 'router'
        cmd = SetGatewayRouter(MyApp(sys.stdout), None)
        args = ['myid', 'externalid']
        self._test_update_resource(resource, cmd, 'myid',
                                   args,
                                   {"external_gateway_info":
                                    {"network_id": "externalid"}}
                                   )

    def test_remove_gateway(self):
        """Remove external gateway from router: externalid"""
        resource = 'router'
        cmd = RemoveGatewayRouter(MyApp(sys.stdout), None)
        args = ['externalid']
        self._test_update_resource(resource, cmd, 'externalid',
                                   args, {"external_gateway_info": {}}
                                   )
