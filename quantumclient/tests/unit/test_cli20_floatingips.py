#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Red Hat
# All Rights Reserved.
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

import sys

from quantumclient.common import exceptions
from quantumclient.quantum.v2_0.floatingip import AssociateFloatingIP
from quantumclient.quantum.v2_0.floatingip import CreateFloatingIP
from quantumclient.quantum.v2_0.floatingip import DeleteFloatingIP
from quantumclient.quantum.v2_0.floatingip import DisassociateFloatingIP
from quantumclient.quantum.v2_0.floatingip import ListFloatingIP
from quantumclient.quantum.v2_0.floatingip import ShowFloatingIP
from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp


class CLITestV20FloatingIps(CLITestV20Base):
    def test_create_floatingip(self):
        """Create floatingip: fip1."""
        resource = 'floatingip'
        cmd = CreateFloatingIP(MyApp(sys.stdout), None)
        name = 'fip1'
        myid = 'myid'
        args = [name]
        position_names = ['floating_network_id']
        position_values = [name]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_floatingip_and_port(self):
        """Create floatingip: fip1."""
        resource = 'floatingip'
        cmd = CreateFloatingIP(MyApp(sys.stdout), None)
        name = 'fip1'
        myid = 'myid'
        pid = 'mypid'
        args = [name, '--port_id', pid]
        position_names = ['floating_network_id', 'port_id']
        position_values = [name, pid]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

        # Test dashed options
        args = [name, '--port-id', pid]
        position_names = ['floating_network_id', 'port_id']
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_floatingip_and_port_and_address(self):
        """Create floatingip: fip1 with a given port and address"""
        resource = 'floatingip'
        cmd = CreateFloatingIP(MyApp(sys.stdout), None)
        name = 'fip1'
        myid = 'myid'
        pid = 'mypid'
        addr = '10.0.0.99'
        args = [name, '--port_id', pid, '--fixed_ip_address', addr]
        position_names = ['floating_network_id', 'port_id', 'fixed_ip_address']
        position_values = [name, pid, addr]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)
        # Test dashed options
        args = [name, '--port-id', pid, '--fixed-ip-address', addr]
        position_names = ['floating_network_id', 'port_id', 'fixed_ip_address']
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_list_floatingips(self):
        """list floatingips: -D."""
        resources = 'floatingips'
        cmd = ListFloatingIP(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_delete_floatingip(self):
        """Delete floatingip: fip1"""
        resource = 'floatingip'
        cmd = DeleteFloatingIP(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_show_floatingip(self):
        """Show floatingip: --fields id."""
        resource = 'floatingip'
        cmd = ShowFloatingIP(MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id'])

    def test_disassociate_ip(self):
        """Disassociate floating IP: myid"""
        resource = 'floatingip'
        cmd = DisassociateFloatingIP(MyApp(sys.stdout), None)
        args = ['myid']
        self._test_update_resource(resource, cmd, 'myid',
                                   args, {"port_id": None}
                                   )

    def test_associate_ip(self):
        """Associate floating IP: myid portid"""
        resource = 'floatingip'
        cmd = AssociateFloatingIP(MyApp(sys.stdout), None)
        args = ['myid', 'portid']
        self._test_update_resource(resource, cmd, 'myid',
                                   args, {"port_id": "portid"}
                                   )
