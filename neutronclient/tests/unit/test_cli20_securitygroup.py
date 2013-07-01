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

import mox

from neutronclient.neutron.v2_0 import securitygroup
from neutronclient.tests.unit import test_cli20


class CLITestV20SecurityGroupsJSON(test_cli20.CLITestV20Base):
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
        args = [name, '--description', description]
        position_names = ['name', 'description']
        position_values = [name, description]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_list_security_groups(self):
        resources = "security_groups"
        cmd = securitygroup.ListSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_security_groups_pagination(self):
        resources = "security_groups"
        cmd = securitygroup.ListSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_security_groups_sort(self):
        resources = "security_groups"
        cmd = securitygroup.ListSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_security_groups_limit(self):
        resources = "security_groups"
        cmd = securitygroup.ListSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

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

    def test_update_security_group(self):
        """Update security group: myid --name myname --description desc."""
        resource = 'security_group'
        cmd = securitygroup.UpdateSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--description', 'mydescription'],
                                   {'name': 'myname',
                                    'description': 'mydescription'}
                                   )

    def test_update_security_group_with_unicode(self):
        resource = 'security_group'
        cmd = securitygroup.UpdateSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', u'\u7f51\u7edc',
                                    '--description', u'\u7f51\u7edc'],
                                   {'name': u'\u7f51\u7edc',
                                    'description': u'\u7f51\u7edc'}
                                   )

    def test_create_security_group_rule_full(self):
        """Create security group rule."""
        resource = 'security_group_rule'
        cmd = securitygroup.CreateSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        direction = 'ingress'
        ethertype = 'IPv4'
        protocol = 'tcp'
        port_range_min = '22'
        port_range_max = '22'
        remote_ip_prefix = '10.0.0.0/24'
        security_group_id = '1'
        remote_group_id = '1'
        args = ['--remote_ip_prefix', remote_ip_prefix, '--direction',
                direction, '--ethertype', ethertype, '--protocol', protocol,
                '--port_range_min', port_range_min, '--port_range_max',
                port_range_max, '--remote_group_id', remote_group_id,
                security_group_id]
        position_names = ['remote_ip_prefix', 'direction', 'ethertype',
                          'protocol', 'port_range_min', 'port_range_max',
                          'remote_group_id', 'security_group_id']
        position_values = [remote_ip_prefix, direction, ethertype, protocol,
                           port_range_min, port_range_max, remote_group_id,
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
        self.mox.StubOutWithMock(securitygroup.ListSecurityGroupRule,
                                 "extend_list")
        securitygroup.ListSecurityGroupRule.extend_list(mox.IsA(list),
                                                        mox.IgnoreArg())
        self._test_list_resources(resources, cmd, True)

    def test_list_security_group_rules_pagination(self):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(securitygroup.ListSecurityGroupRule,
                                 "extend_list")
        securitygroup.ListSecurityGroupRule.extend_list(mox.IsA(list),
                                                        mox.IgnoreArg())
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_security_group_rules_sort(self):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(securitygroup.ListSecurityGroupRule,
                                 "extend_list")
        securitygroup.ListSecurityGroupRule.extend_list(mox.IsA(list),
                                                        mox.IgnoreArg())
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_security_group_rules_limit(self):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(securitygroup.ListSecurityGroupRule,
                                 "extend_list")
        securitygroup.ListSecurityGroupRule.extend_list(mox.IsA(list),
                                                        mox.IgnoreArg())
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_show_security_group_rule(self):
        resource = 'security_group_rule'
        cmd = securitygroup.ShowSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id'])

    def _test_list_security_group_rules_extend(self, data=None, expected=None,
                                               args=[], conv=True,
                                               query_field=False):
        def setup_list_stub(resources, data, query):
            reses = {resources: data}
            resstr = self.client.serialize(reses)
            resp = (test_cli20.MyResp(200), resstr)
            path = getattr(self.client, resources + '_path')
            self.client.httpclient.request(
                test_cli20.end_url(path, query), 'GET',
                body=None,
                headers=mox.ContainsKeyValue(
                    'X-Auth-Token', test_cli20.TOKEN)).AndReturn(resp)

        # Setup the default data
        _data = {'cols': ['id', 'security_group_id', 'remote_group_id'],
                 'data': [('ruleid1', 'myid1', 'myid1'),
                          ('ruleid2', 'myid2', 'myid3'),
                          ('ruleid3', 'myid2', 'myid2')]}
        _expected = {'cols': ['id', 'security_group', 'remote_group'],
                     'data': [('ruleid1', 'group1', 'group1'),
                              ('ruleid2', 'group2', 'group3'),
                              ('ruleid3', 'group2', 'group2')]}
        if data is None:
            data = _data
        list_data = [dict(zip(data['cols'], d)) for d in data['data']]
        if expected is None:
            expected = {}
        expected['cols'] = expected.get('cols', _expected['cols'])
        expected['data'] = expected.get('data', _expected['data'])

        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(cmd, 'get_client')
        self.mox.StubOutWithMock(self.client.httpclient, 'request')
        cmd.get_client().AndReturn(self.client)
        query = ''
        if query_field:
            query = '&'.join(['fields=' + f for f in data['cols']])
        setup_list_stub('security_group_rules', list_data, query)
        if conv:
            cmd.get_client().AndReturn(self.client)
            sec_ids = set()
            for n in data['data']:
                sec_ids.add(n[1])
                sec_ids.add(n[2])
            filters = ''
            for id in sec_ids:
                filters = filters + "&id=%s" % id
            setup_list_stub('security_groups',
                            [{'id': 'myid1', 'name': 'group1'},
                             {'id': 'myid2', 'name': 'group2'},
                             {'id': 'myid3', 'name': 'group3'}],
                            query='fields=id&fields=name' + filters)
        self.mox.ReplayAll()

        cmd_parser = cmd.get_parser('list_security_group_rules')
        parsed_args = cmd_parser.parse_args(args)
        result = cmd.get_data(parsed_args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        # Check columns
        self.assertEqual(result[0], expected['cols'])
        # Check data
        _result = [x for x in result[1]]
        self.assertEqual(len(_result), len(expected['data']))
        for res, exp in zip(_result, expected['data']):
            self.assertEqual(len(res), len(exp))
            self.assertEqual(res, exp)

    def test_list_security_group_rules_extend_source_id(self):
        self._test_list_security_group_rules_extend()

    def test_list_security_group_rules_extend_no_nameconv(self):
        expected = {'cols': ['id', 'security_group_id', 'remote_group_id'],
                    'data': [('ruleid1', 'myid1', 'myid1'),
                             ('ruleid2', 'myid2', 'myid3'),
                             ('ruleid3', 'myid2', 'myid2')]}
        args = ['--no-nameconv']
        self._test_list_security_group_rules_extend(expected=expected,
                                                    args=args, conv=False)

    def test_list_security_group_rules_extend_with_columns(self):
        args = '-c id -c security_group_id -c remote_group_id'.split()
        self._test_list_security_group_rules_extend(args=args)

    def test_list_security_group_rules_extend_with_columns_no_id(self):
        args = '-c id -c security_group -c remote_group'.split()
        self._test_list_security_group_rules_extend(args=args)

    def test_list_security_group_rules_extend_with_fields(self):
        args = '-F id -F security_group_id -F remote_group_id'.split()
        self._test_list_security_group_rules_extend(args=args,
                                                    query_field=True)

    def test_list_security_group_rules_extend_with_fields_no_id(self):
        args = '-F id -F security_group -F remote_group'.split()
        self._test_list_security_group_rules_extend(args=args,
                                                    query_field=True)


class CLITestV20SecurityGroupsXML(CLITestV20SecurityGroupsJSON):
    format = 'xml'
