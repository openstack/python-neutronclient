#!/usr/bin/env python
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

import mock
from oslo_utils import uuidutils
import six

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron.v2_0 import securitygroup
from neutronclient.tests.unit import test_cli20


class CLITestV20SecurityGroupsJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['security_group', 'security_group_rule']

    def test_create_security_group(self):
        # Create security group: webservers.
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
        # Create security group: webservers.
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
        # Create security group: webservers.
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
        # Delete security group: myid.
        resource = 'security_group'
        cmd = securitygroup.DeleteSecurityGroup(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_update_security_group(self):
        # Update security group: myid --name myname --description desc.
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
        # Create security group rule.
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
                security_group_id, '--description', 'PCI policy 1421912']
        position_names = ['remote_ip_prefix', 'direction', 'ethertype',
                          'protocol', 'port_range_min', 'port_range_max',
                          'remote_group_id', 'security_group_id']
        position_values = [remote_ip_prefix, direction, ethertype, protocol,
                           port_range_min, port_range_max, remote_group_id,
                           security_group_id]
        self._test_create_resource(resource, cmd, None, myid, args,
                                   position_names, position_values,
                                   description='PCI policy 1421912')

    def test_create_security_group_rule_with_integer_protocol_value(self):
        resource = 'security_group_rule'
        cmd = securitygroup.CreateSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        direction = 'ingress'
        ethertype = 'IPv4'
        protocol = '2'
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
        # Delete security group rule: myid.
        resource = 'security_group_rule'
        cmd = securitygroup.DeleteSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    @mock.patch.object(securitygroup.ListSecurityGroupRule, "extend_list")
    def test_list_security_group_rules(self, mock_extend_list):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def _build_test_data(self, data, excess=0):
        # Length of a query filter on security group rule id
        # in these testcases, id='secgroupid%02d' (with len(id)=12)
        sec_group_id_filter_len = 12

        response = []
        replace_rules = {'security_group_id': 'security_group',
                         'remote_group_id': 'remote_group'}

        search_opts = {'fields': ['id', 'name']}
        sec_group_ids = set()
        for rule in data:
            for key in replace_rules:
                if rule.get(key):
                    sec_group_ids.add(rule[key])
                    response.append({'id': rule[key], 'name': 'default'})
        sec_group_ids = list(sec_group_ids)

        result = []

        sec_group_count = len(sec_group_ids)
        max_size = ((sec_group_id_filter_len * sec_group_count) - excess)
        chunk_size = max_size // sec_group_id_filter_len

        for i in range(0, sec_group_count, chunk_size):
            search_opts['id'] = sec_group_ids[i: i + chunk_size]
            params = utils.safe_encode_dict(search_opts)
            resp_str = self.client.serialize({'security_groups': response})

            result.append({
                'filter': six.moves.urllib.parse.urlencode(params, doseq=1),
                'response': (test_cli20.MyResp(200), resp_str),
            })

        return result

    def test_extend_list(self):
        data = [{'name': 'default',
                 'remote_group_id': 'remgroupid%02d' % i}
                for i in range(10)]
        data.append({'name': 'default', 'remote_group_id': None})
        resources = "security_groups"

        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)

        path = getattr(self.client, resources + '_path')
        responses = self._build_test_data(data)
        known_args, _vs = cmd.get_parser(
            'list' + resources).parse_known_args()
        resp = responses[0]['response']

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            cmd.extend_list(data, known_args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(test_cli20.end_url(
                path, responses[0]['filter']), self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))

    def test_extend_list_exceed_max_uri_len(self):
        data = [{'name': 'default',
                 'security_group_id': 'secgroupid%02d' % i,
                 'remote_group_id': 'remgroupid%02d' % i}
                for i in range(10)]
        data.append({'name': 'default',
                     'security_group_id': 'secgroupid10',
                     'remote_group_id': None})
        resources = "security_groups"

        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        path = getattr(self.client, resources + '_path')
        responses = self._build_test_data(data, excess=1)

        known_args, _vs = cmd.get_parser(
            'list' + resources).parse_known_args()
        mock_request_side_effects = []
        mock_request_calls = []
        mock_check_uri_side_effects = [exceptions.RequestURITooLong(excess=1)]
        mock_check_uri_calls = [mock.call(mock.ANY)]
        for item in responses:
            mock_request_side_effects.append(item['response'])
            mock_request_calls.append(mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(path, item['filter']), self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN})))
            mock_check_uri_side_effects.append(None)
            mock_check_uri_calls.append(mock.call(mock.ANY))

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient,
                                  "request") as mock_request, \
                mock.patch.object(self.client.httpclient,
                                  "_check_uri_length") as mock_check_uri:
            mock_request.side_effect = mock_request_side_effects
            mock_check_uri.side_effect = mock_check_uri_side_effects
            cmd.extend_list(data, known_args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_has_calls(mock_request_calls)
        mock_check_uri.assert_has_calls(mock_check_uri_calls)
        self.assertEqual(len(mock_request_calls), mock_request.call_count)
        self.assertEqual(len(mock_check_uri_calls), mock_check_uri.call_count)

    @mock.patch.object(securitygroup.ListSecurityGroupRule, "extend_list")
    def test_list_security_group_rules_pagination(self, mock_extend_list):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    @mock.patch.object(securitygroup.ListSecurityGroupRule, "extend_list")
    def test_list_security_group_rules_sort(self, mock_extend_list):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    @mock.patch.object(securitygroup.ListSecurityGroupRule, "extend_list")
    def test_list_security_group_rules_limit(self, mock_extend_list):
        resources = "security_group_rules"
        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def test_show_security_group_rule(self):
        resource = 'security_group_rule'
        cmd = securitygroup.ShowSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id'])

    def _test_list_security_group_rules_extend(self, api_data, expected,
                                               args=(), conv=True,
                                               query_fields=None):
        def setup_list_stub(resources, data, query, mock_calls, mock_returns):
            reses = {resources: data}
            resstr = self.client.serialize(reses)
            resp = (test_cli20.MyResp(200), resstr)
            path = getattr(self.client, resources + '_path')
            mock_calls.append(mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(path, query),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN})))
            mock_returns.append(resp)

        cmd = securitygroup.ListSecurityGroupRule(
            test_cli20.MyApp(sys.stdout), None)
        query = ''
        if query_fields:
            query = '&'.join(['fields=' + f for f in query_fields])
        mock_request_calls = []
        mock_request_returns = []
        setup_list_stub('security_group_rules', api_data, query,
                        mock_request_calls, mock_request_returns)
        if conv:
            sec_ids = set()
            for n in api_data:
                sec_ids.add(n['security_group_id'])
                if n.get('remote_group_id'):
                    sec_ids.add(n['remote_group_id'])
            filters = ''
            for id in sec_ids:
                filters = filters + "&id=%s" % id
            setup_list_stub('security_groups',
                            [{'id': 'myid1', 'name': 'group1'},
                             {'id': 'myid2', 'name': 'group2'},
                             {'id': 'myid3', 'name': 'group3'}],
                            'fields=id&fields=name' + filters,
                            mock_request_calls,
                            mock_request_returns)

        cmd_parser = cmd.get_parser('list_security_group_rules')
        parsed_args = cmd_parser.parse_args(args)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient,
                                  "request") as mock_request:
            mock_request.side_effect = mock_request_returns
            result = cmd.take_action(parsed_args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_has_calls(mock_request_calls)
        self.assertEqual(len(mock_request_calls), mock_request.call_count)
        self.assertEqual(expected['cols'], result[0])
        # Check data
        _result = [x for x in result[1]]
        self.assertEqual(len(expected['data']), len(_result))
        for res, exp in zip(_result, expected['data']):
            self.assertEqual(len(exp), len(res))
            self.assertEqual(exp, res)

    def _test_list_security_group_rules_extend_sg_name(
            self, expected_mode=None, args=(), conv=True, query_field=False):
        if query_field:
            field_filters = ['id', 'security_group_id',
                             'remote_ip_prefix', 'remote_group_id']
        else:
            field_filters = None

        data = [self._prepare_rule(rule_id='ruleid1', sg_id='myid1',
                                   remote_group_id='myid1',
                                   filters=field_filters),
                self._prepare_rule(rule_id='ruleid2', sg_id='myid2',
                                   remote_group_id='myid3',
                                   filters=field_filters),
                self._prepare_rule(rule_id='ruleid3', sg_id='myid2',
                                   remote_group_id='myid2',
                                   filters=field_filters),
                ]

        if expected_mode == 'noconv':
            expected = {'cols': ['id', 'security_group_id', 'remote_group_id'],
                        'data': [('ruleid1', 'myid1', 'myid1'),
                                 ('ruleid2', 'myid2', 'myid3'),
                                 ('ruleid3', 'myid2', 'myid2')]}
        elif expected_mode == 'remote_group_id':
            expected = {'cols': ['id', 'security_group', 'remote_group'],
                        'data': [('ruleid1', 'group1', 'group1'),
                                 ('ruleid2', 'group2', 'group3'),
                                 ('ruleid3', 'group2', 'group2')]}
        else:
            expected = {'cols': ['id', 'security_group', 'remote'],
                        'data': [('ruleid1', 'group1', 'group1 (group)'),
                                 ('ruleid2', 'group2', 'group3 (group)'),
                                 ('ruleid3', 'group2', 'group2 (group)')]}

        self._test_list_security_group_rules_extend(
            data, expected, args=args, conv=conv, query_fields=field_filters)

    def test_list_security_group_rules_extend_remote_sg_name(self):
        args = '-c id -c security_group -c remote'.split()
        self._test_list_security_group_rules_extend_sg_name(args=args)

    def test_list_security_group_rules_extend_sg_name_noconv(self):
        args = '--no-nameconv -c id -c security_group_id -c remote_group_id'
        args = args.split()
        self._test_list_security_group_rules_extend_sg_name(
            expected_mode='noconv', args=args, conv=False)

    def test_list_security_group_rules_extend_sg_name_with_columns(self):
        args = '-c id -c security_group_id -c remote_group_id'.split()
        self._test_list_security_group_rules_extend_sg_name(
            expected_mode='remote_group_id', args=args)

    def test_list_security_group_rules_extend_sg_name_with_columns_no_id(self):
        args = '-c id -c security_group -c remote_group'.split()
        self._test_list_security_group_rules_extend_sg_name(
            expected_mode='remote_group_id', args=args)

    def test_list_security_group_rules_extend_sg_name_with_fields(self):
        # NOTE: remote_ip_prefix is required to show "remote" column
        args = ('-F id -F security_group_id '
                '-F remote_ip_prefix -F remote_group_id').split()
        self._test_list_security_group_rules_extend_sg_name(
            args=args, query_field=True)

    def test_list_security_group_rules_extend_sg_name_with_fields_no_id(self):
        # NOTE: remote_ip_prefix is required to show "remote" column
        args = ('-F id -F security_group '
                '-F remote_ip_prefix -F remote_group').split()
        self._test_list_security_group_rules_extend_sg_name(args=args,
                                                            query_field=True)

    def test_list_security_group_rules_extend_remote(self):
        args = '-c id -c security_group -c remote'.split()

        data = [self._prepare_rule(rule_id='ruleid1', sg_id='myid1',
                                   remote_ip_prefix='172.16.18.0/24'),
                self._prepare_rule(rule_id='ruleid2', sg_id='myid2',
                                   remote_ip_prefix='172.16.20.0/24'),
                self._prepare_rule(rule_id='ruleid3', sg_id='myid2',
                                   remote_group_id='myid3')]
        expected = {'cols': ['id', 'security_group', 'remote'],
                    'data': [('ruleid1', 'group1', '172.16.18.0/24 (CIDR)'),
                             ('ruleid2', 'group2', '172.16.20.0/24 (CIDR)'),
                             ('ruleid3', 'group2', 'group3 (group)')]}
        self._test_list_security_group_rules_extend(data, expected, args)

    def test_list_security_group_rules_extend_proto_port(self):
        data = [self._prepare_rule(rule_id='ruleid1', sg_id='myid1',
                                   protocol='tcp',
                                   port_range_min=22, port_range_max=22),
                self._prepare_rule(rule_id='ruleid2', sg_id='myid2',
                                   direction='egress', ethertype='IPv6',
                                   protocol='udp',
                                   port_range_min=80, port_range_max=81),
                self._prepare_rule(rule_id='ruleid3', sg_id='myid2',
                                   protocol='icmp',
                                   remote_ip_prefix='10.2.0.0/16')]
        expected = {
            'cols': ['id', 'security_group', 'direction', 'ethertype',
                     'port/protocol', 'remote'],
            'data': [
                ('ruleid1', 'group1', 'ingress', 'IPv4', '22/tcp', 'any'),
                ('ruleid2', 'group2', 'egress', 'IPv6', '80-81/udp', 'any'),
                ('ruleid3', 'group2', 'ingress', 'IPv4', 'icmp',
                 '10.2.0.0/16 (CIDR)')
            ]}
        self._test_list_security_group_rules_extend(data, expected)

    def _prepare_rule(self, rule_id=None, sg_id=None, tenant_id=None,
                      direction=None, ethertype=None,
                      protocol=None, port_range_min=None, port_range_max=None,
                      remote_ip_prefix=None, remote_group_id=None,
                      filters=None):
        rule = {'id': rule_id or uuidutils.generate_uuid(),
                'tenant_id': tenant_id or uuidutils.generate_uuid(),
                'security_group_id': sg_id or uuidutils.generate_uuid(),
                'direction': direction or 'ingress',
                'ethertype': ethertype or 'IPv4',
                'protocol': protocol,
                'port_range_min': port_range_min,
                'port_range_max': port_range_max,
                'remote_ip_prefix': remote_ip_prefix,
                'remote_group_id': remote_group_id}
        if filters:
            return dict([(k, v) for k, v in rule.items() if k in filters])
        else:
            return rule

    def test__get_remote_both_unspecified(self):
        sg_rule = self._prepare_rule(remote_ip_prefix=None,
                                     remote_group_id=None)
        self.assertIsNone(securitygroup._get_remote(sg_rule))

    def test__get_remote_remote_ip_prefix_specified(self):
        sg_rule = self._prepare_rule(remote_ip_prefix='172.16.18.0/24')
        self.assertEqual('172.16.18.0/24 (CIDR)',
                         securitygroup._get_remote(sg_rule))

    def test__get_remote_remote_group_specified(self):
        sg_rule = self._prepare_rule(remote_group_id='sg_id1')
        self.assertEqual('sg_id1 (group)', securitygroup._get_remote(sg_rule))

    def test__get_protocol_port_all_none(self):
        sg_rule = self._prepare_rule()
        self.assertIsNone(securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_tcp_all_port(self):
        sg_rule = self._prepare_rule(protocol='tcp')
        self.assertEqual('tcp', securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_tcp_one_port(self):
        sg_rule = self._prepare_rule(protocol='tcp',
                                     port_range_min=22, port_range_max=22)
        self.assertEqual('22/tcp', securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_tcp_port_range(self):
        sg_rule = self._prepare_rule(protocol='tcp',
                                     port_range_min=5000, port_range_max=5010)
        self.assertEqual('5000-5010/tcp',
                         securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_udp_all_port(self):
        sg_rule = self._prepare_rule(protocol='udp')
        self.assertEqual('udp', securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_udp_one_port(self):
        sg_rule = self._prepare_rule(protocol='udp',
                                     port_range_min=22, port_range_max=22)
        self.assertEqual('22/udp', securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_udp_port_range(self):
        sg_rule = self._prepare_rule(protocol='udp',
                                     port_range_min=5000, port_range_max=5010)
        self.assertEqual('5000-5010/udp',
                         securitygroup._get_protocol_port(sg_rule))

    def test__get_protocol_port_icmp_all(self):
        sg_rule = self._prepare_rule(protocol='icmp')
        self.assertEqual('icmp', securitygroup._get_protocol_port(sg_rule))

    def test_get_ethertype_for_protocol_icmpv6(self):
        self.assertEqual('IPv6',
                         securitygroup.generate_default_ethertype('icmpv6'))

    def test_get_ethertype_for_protocol_icmp(self):
        self.assertEqual('IPv4',
                         securitygroup.generate_default_ethertype('icmp'))

    def test__get_protocol_port_udp_code_type(self):
        sg_rule = self._prepare_rule(protocol='icmp',
                                     port_range_min=1, port_range_max=8)
        self.assertEqual('icmp (type:1, code:8)',
                         securitygroup._get_protocol_port(sg_rule))

    def test__format_sg_rules(self):
        rules = [self._prepare_rule(),
                 self._prepare_rule(protocol='tcp', port_range_min=80,
                                    port_range_max=80),
                 self._prepare_rule(remote_ip_prefix='192.168.1.0/24'),
                 self._prepare_rule(remote_group_id='group1'),
                 self._prepare_rule(protocol='tcp',
                                    remote_ip_prefix='10.1.1.0/24'),
                 self._prepare_rule(direction='egress'),
                 self._prepare_rule(direction='egress', ethertype='IPv6'),
                 ]
        sg = {'security_group_rules': rules}
        expected_data = ['ingress, IPv4',
                         'ingress, IPv4, 80/tcp',
                         'ingress, IPv4, remote_ip_prefix: 192.168.1.0/24',
                         'ingress, IPv4, remote_group_id: group1',
                         'ingress, IPv4, tcp, remote_ip_prefix: 10.1.1.0/24',
                         'egress, IPv4',
                         'egress, IPv6',
                         ]
        expected = '\n'.join(sorted(expected_data))
        self.assertEqual(expected, securitygroup._format_sg_rules(sg))
