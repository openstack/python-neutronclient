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

from quantumclient.quantum.v2_0 import securitygroup
from quantumclient.tests.unit import test_cli20


class CLITestV20SecurityGroups(test_cli20.CLITestV20Base):
    def test_create_security_group(self):
        """Create security group: webservers."""
        resource = 'security_group'
        cmd = securitygroup.CreateSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        name = 'webservers'
        myid = 'myid'
        args = [name, ]
        position_names = ['name']
        position_values = [name]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_security_group_tenant(self):
        """Create security group: webservers."""
        resource = 'security_group'
        cmd = securitygroup.CreateSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        name = 'webservers'
        description = 'my webservers'
        myid = 'myid'
        args = ['--tenant_id', 'tenant_id', '--description', description, name]
        position_names = ['name', 'description']
        position_values = [name, description]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenant_id')

    def test_create_security_group_with_description(self):
        """Create security group: webservers."""
        resource = 'security_group'
        cmd = securitygroup.CreateSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        name = 'webservers'
        description = 'my webservers'
        myid = 'myid'
        args = [name,  '--description', description]
        position_names = ['name', 'description']
        position_values = [name, description]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_list_security_groups(self):
        resources = "security_groups"
        cmd = securitygroup.ListSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_show_security_group_id(self):
        resource = 'security_group'
        cmd = securitygroup.ShowSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id'])

    def test_show_security_group_id_name(self):
        resource = 'security_group'
        cmd = securitygroup.ShowSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_delete_security_group(self):
        """Delete security group: myid."""
        resource = 'security_group'
        cmd = securitygroup.DeleteSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_create_security_group_rule_full(self):
        """Create security group rule"""
        resource = 'security_group_rule'
        cmd = securitygroup.CreateSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        direction = 'ingress'
        ethertype = 'IPv4'
        protocol = 'tcp'
        port_range_min = '22'
        port_range_max = '22'
        source_ip_prefix = '10.0.0.0/24'
        security_group_id = '1'
        source_group_id = '1'
        args = ['--source_ip_prefix', source_ip_prefix, '--direction',
                direction, '--ethertype', ethertype, '--protocol', protocol,
                '--port_range_min', port_range_min, '--port_range_max',
                port_range_max, '--source_group_id', source_group_id,
                security_group_id]
        position_names = ['source_ip_prefix', 'direction', 'ethertype',
                          'protocol', 'port_range_min', 'port_range_max',
                          'source_group_id', 'security_group_id']
        position_values = [source_ip_prefix, direction, ethertype, protocol,
                           port_range_min, port_range_max, source_group_id,
                           security_group_id]
        self._test_create_resource(resource, cmd, None, myid, args,
                                   position_names, position_values)

    def test_delete_security_group_rule(self):
        """Delete security group rule: myid."""
        resource = 'security_group_rule'
        cmd = securitygroup.DeleteSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_list_security_group_rules(self):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_show_security_group_rule(self):
        resource = 'security_group_rule'
        cmd = securitygroup.ShowSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id'])
