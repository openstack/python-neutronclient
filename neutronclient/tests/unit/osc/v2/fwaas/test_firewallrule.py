# Copyright 2016 FUJITSU LIMITED
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

import re
from unittest import mock

from osc_lib import exceptions
from osc_lib.tests import utils
import testtools

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.fwaas import firewallrule
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.fwaas import common
from neutronclient.tests.unit.osc.v2.fwaas import fakes


_fwr = fakes.FirewallRule().create()
CONVERT_MAP = {
    'project': 'tenant_id',
    'enable_rule': 'enabled',
    'disable_rule': 'enabled',
    'share': 'shared',
    'no_share': 'shared',
    'source_firewall_group': 'source_firewall_group_id',
    'destination_firewall_group': 'destination_firewall_group_id',
    'no_source_firewall_group': 'source_firewall_group_id',
    'no_destination_firewall_group': 'destination_firewall_group_id',
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _fwr
    if data:
        source.update(data)
    ret = tuple(_replace_display_columns(key, source[key]) for key in source)
    return ret


def _replace_display_columns(key, val):
    if key == 'protocol':
        return firewallrule.ProtocolColumn(val)
    return val


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = _fwr
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        if re.match('^no_', key) and val is True:
            new_value = None
        elif (key == 'enable' or key == 'enable_rule') and val:
            new_value = True
        elif (key == 'disable' or key == 'disable_rule') and val:
            new_value = False
        elif (key == 'protocol' and val and val.lower() == 'any'):
            new_value = None
        elif val is True or val is False:
            new_value = val
        elif key in ('name', 'description'):
            new_value = val
        else:
            new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestFirewallRule(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req=None, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = exp_req
        if not exp_req:
            self.mocked.assert_called_once_with()
        else:
            self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, headers)

    def setUp(self):
        super(TestFirewallRule, self).setUp()

        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _fwr['tenant_id']
        self.res = 'firewall_rule'
        self.res_plural = 'firewall_rules'
        self.resource = _fwr
        self.headers = (
            'ID',
            'Name',
            'Enabled',
            'Description',
            'Firewall Policy',
            'IP Version',
            'Action',
            'Protocol',
            'Source IP Address',
            'Source Port',
            'Destination IP Address',
            'Destination Port',
            'Shared',
            'Project',
            'Source Firewall Group ID',
            'Destination Firewall Group ID',
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Action',
            'Description',
            'Destination Firewall Group ID',
            'Destination IP Address',
            'Destination Port',
            'Enabled',
            'Firewall Policy',
            'ID',
            'IP Version',
            'Name',
            'Project',
            'Protocol',
            'Shared',
            'Source Firewall Group ID',
            'Source IP Address',
            'Source Port',
            'Summary',
        )
        self.ordered_data = (
            _fwr['action'],
            _fwr['description'],
            _fwr['destination_firewall_group_id'],
            _fwr['destination_ip_address'],
            _fwr['destination_port'],
            _fwr['firewall_policy_id'],
            _fwr['enabled'],
            _fwr['id'],
            _fwr['ip_version'],
            _fwr['name'],
            _fwr['tenant_id'],
            _replace_display_columns('protocol', _fwr['protocol']),
            _fwr['shared'],
            _fwr['source_firewall_group_id'],
            _fwr['source_ip_address'],
            _fwr['source_port'],
        )
        self.ordered_columns = (
            'action',
            'description',
            'destination_firewall_group_id',
            'destination_ip_address',
            'destination_port',
            'enabled',
            'id',
            'ip_version',
            'name',
            'tenant_id',
            'protocol',
            'shared',
            'source_firewall_group_id',
            'source_ip_address',
            'source_port',
        )


class TestCreateFirewallRule(TestFirewallRule, common.TestCreateFWaaS):

    def setUp(self):
        super(TestCreateFirewallRule, self).setUp()
        self.networkclient.create_firewall_rule = mock.Mock(
            return_value=_fwr)
        self.mocked = self.networkclient.create_firewall_rule

        def _mock_find_group(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_group.side_effect = _mock_find_group

        self.cmd = firewallrule.CreateFirewallRule(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.networkclient.create_firewall_rule.return_value = response
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            _replace_display_columns(column, response[column])
            for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name') or 'my-name'
        description = args.get('description') or 'my-desc'
        source_ip = args.get('source_ip_address') or '192.168.1.0/24'
        destination_ip = args.get('destination_ip_address') or '192.168.2.0/24'
        source_port = args.get('source_port') or '0:65535'
        protocol = args.get('protocol') or 'udp'
        action = args.get('action') or 'deny'
        ip_version = args.get('ip_version') or '4'
        destination_port = args.get('destination_port') or '0:65535'
        destination_firewall_group = args.get(
            'destination_firewall_group') or 'my-dst-fwg'
        source_firewall_group = args.get(
            'source_firewall_group') or 'my-src-fwg'
        tenant_id = args.get('tenant_id') or 'my-tenant'
        arglist = [
            '--description', description,
            '--name', name,
            '--protocol', protocol,
            '--ip-version', ip_version,
            '--source-ip-address', source_ip,
            '--destination-ip-address', destination_ip,
            '--source-port', source_port,
            '--destination-port', destination_port,
            '--action', action,
            '--project', tenant_id,
            '--disable-rule',
            '--share',
            '--source-firewall-group', source_firewall_group,
            '--destination-firewall-group', destination_firewall_group
        ]

        verifylist = [
            ('name', name),
            ('description', description),
            ('share', True),
            ('protocol', protocol),
            ('ip_version', ip_version),
            ('source_ip_address', source_ip),
            ('destination_ip_address', destination_ip),
            ('source_port', source_port),
            ('destination_port', destination_port),
            ('action', action),
            ('disable_rule', True),
            ('project', tenant_id),
            ('source_firewall_group', source_firewall_group),
            ('destination_firewall_group', destination_firewall_group)
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self, args={}):
        arglist, verifylist = self._set_all_params(args)
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.check_results(headers, data, None)

    def test_create_with_all_params(self):
        self._test_create_with_all_params()

    def test_create_with_all_params_protocol_any(self):
        self._test_create_with_all_params({'protocol': 'any'})

    def test_create_with_all_params_ip_version_6(self):
        self._test_create_with_all_params({'ip_version': '6'})

    def test_create_with_all_params_invalid_ip_version(self):
        arglist, verifylist = self._set_all_params({'ip_version': '128'})
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_all_params_action_upper_capitalized(self):
        for action in ('Allow', 'DENY', 'Reject'):
            arglist, verifylist = self._set_all_params({'action': action})
            self.assertRaises(
                testtools.matchers._impl.MismatchError,
                self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_all_params_protocol_upper_capitalized(self):
        for protocol in ('TCP', 'Tcp', 'ANY', 'AnY', 'iCMp'):
            arglist, verifylist = self._set_all_params({'protocol': protocol})
            self.assertRaises(
                testtools.matchers._impl.MismatchError,
                self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_src_fwg_and_no(self):
        fwg = 'my-fwg'
        arglist = [
            '--source-firewall-group', fwg,
            '--no-source-firewall-group',
        ]
        verifylist = [
            ('source_firewall_group', fwg),
            ('no_source_firewall_group', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_dst_fwg_and_no(self):
        fwg = 'my-fwg'
        arglist = [
            '--destination-firewall-group', fwg,
            '--no-destination-firewall-group',
        ]
        verifylist = [
            ('destination_firewall_group', fwg),
            ('no_destination_firewall_group', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestListFirewallRule(TestFirewallRule):

    def _setup_summary(self, expect=None):
        protocol = (_fwr['protocol'] or 'any').upper()
        src = 'source(port): 192.168.1.0/24(1:11111)'
        dst = 'dest(port): 192.168.2.2(2:22222)'
        action = 'deny'
        if expect:
            if expect.get('protocol'):
                protocol = expect['protocol']
            if expect.get('source_ip_address'):
                src_ip = expect['source_ip_address']
            if expect.get('source_port'):
                src_port = expect['source_port']
            if expect.get('destination_ip_address'):
                dst_ip = expect['destination_ip_address']
            if expect.get('destination_port'):
                dst_port = expect['destination_port']
            if expect.get('action'):
                action = expect['action']
            src = 'source(port): ' + src_ip + '(' + src_port + ')'
            dst = 'dest(port): ' + dst_ip + '(' + dst_port + ')'
        return ',\n '.join([protocol, src, dst, action])

    def setUp(self):
        super(TestListFirewallRule, self).setUp()
        self.cmd = firewallrule.ListFirewallRule(self.app, self.namespace)

        self.short_header = (
            'ID',
            'Name',
            'Enabled',
            'Summary',
            'Firewall Policy',
        )

        summary = self._setup_summary(_fwr)

        self.short_data = (
            _fwr['id'],
            _fwr['name'],
            _fwr['enabled'],
            summary,
            _fwr['firewall_policy_id']
        )
        self.networkclient.firewall_rules = mock.Mock(
            return_value=[_fwr])
        self.mocked = self.networkclient.firewall_rules

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertListItemEqual([self.short_data], list(data))


class TestShowFirewallRule(TestFirewallRule, common.TestShowFWaaS):

    def setUp(self):
        super(TestShowFirewallRule, self).setUp()
        self.networkclient.get_firewall_rule = mock.Mock(
            return_value=_fwr)
        self.mocked = self.networkclient.get_firewall_rule
        self.cmd = firewallrule.ShowFirewallRule(self.app, self.namespace)


class TestSetFirewallRule(TestFirewallRule, common.TestSetFWaaS):

    def setUp(self):
        super(TestSetFirewallRule, self).setUp()
        self.networkclient.update_firewall_rule = mock.Mock(
            return_value=_fwr)
        self.mocked = self.networkclient.update_firewall_rule

        def _mock_find_rule(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = firewallrule.SetFirewallRule(self.app, self.namespace)

    def test_set_protocol_with_any(self):
        target = self.resource['id']
        protocol = 'any'
        arglist = [target, '--protocol', protocol]
        verifylist = [
            (self.res, target),
            ('protocol', protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'protocol': None})
        self.assertIsNone(result)

    def test_set_protocol_with_udp(self):
        target = self.resource['id']
        protocol = 'udp'
        arglist = [target, '--protocol', protocol]
        verifylist = [
            (self.res, target),
            ('protocol', protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'protocol': protocol})
        self.assertIsNone(result)

    def test_set_source_ip_address(self):
        target = self.resource['id']
        src_ip = '192.192.192.192'
        arglist = [target, '--source-ip-address', src_ip]
        verifylist = [
            (self.res, target),
            ('source_ip_address', src_ip),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_ip_address': src_ip})
        self.assertIsNone(result)

    def test_set_source_port(self):
        target = self.resource['id']
        src_port = '32678'
        arglist = [target, '--source-port', src_port]
        verifylist = [
            (self.res, target),
            ('source_port', src_port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_port': src_port})
        self.assertIsNone(result)

    def test_set_destination_ip_address(self):
        target = self.resource['id']
        dst_ip = '0.1.0.1'
        arglist = [target, '--destination-ip-address', dst_ip]
        verifylist = [
            (self.res, target),
            ('destination_ip_address', dst_ip),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_ip_address': dst_ip})
        self.assertIsNone(result)

    def test_set_destination_port(self):
        target = self.resource['id']
        dst_port = '65432'
        arglist = [target, '--destination-port', dst_port]
        verifylist = [
            (self.res, target),
            ('destination_port', dst_port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_port': dst_port})
        self.assertIsNone(result)

    def test_set_enable_rule(self):
        target = self.resource['id']
        arglist = [target, '--enable-rule']
        verifylist = [
            (self.res, target),
            ('enable_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'enabled': True})
        self.assertIsNone(result)

    def test_set_disable_rule(self):
        target = self.resource['id']
        arglist = [target, '--disable-rule']
        verifylist = [
            (self.res, target),
            ('disable_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'enabled': False})
        self.assertIsNone(result)

    def test_set_action(self):
        target = self.resource['id']
        action = 'reject'
        arglist = [target, '--action', action]
        verifylist = [
            (self.res, target),
            ('action', action),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'action': action})
        self.assertIsNone(result)

    def test_set_enable_rule_and_disable_rule(self):
        target = self.resource['id']
        arglist = [target, '--enable-rule', '--disable-rule']
        verifylist = [
            (self.res, target),
            ('enable_rule', True),
            ('disable_rule', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_no_source_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-source-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('no_source_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_ip_address': None})
        self.assertIsNone(result)

    def test_set_no_source_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-source-port',
        ]
        verifylist = [
            (self.res, target),
            ('no_source_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'source_port': None})
        self.assertIsNone(result)

    def test_set_no_destination_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-destination-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('no_destination_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_ip_address': None})
        self.assertIsNone(result)

    def test_set_no_destination_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-destination-port',
        ]
        verifylist = [
            (self.res, target),
            ('no_destination_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_port': None})
        self.assertIsNone(result)

    def test_set_source_ip_address_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-ip-address', '192.168.1.0/24',
            '--no-source-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('source_ip_address', '192.168.1.0/24'),
            ('no_source_ip_address', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_destination_ip_address_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-ip-address', '192.168.2.0/24',
            '--no-destination-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('destination_ip_address', '192.168.2.0/24'),
            ('no_destination_ip_address', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_source_port_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-port', '1:12345',
            '--no-source-port',
        ]
        verifylist = [
            (self.res, target),
            ('source_port', '1:12345'),
            ('no_source_port', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_destination_port_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-port', '1:54321',
            '--no-destination-port',
        ]
        verifylist = [
            (self.res, target),
            ('destination_port', '1:54321'),
            ('no_destination_port', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_and_raises(self):
        self.networkclient.update_firewall_rule = mock.Mock(
            side_effect=Exception)
        target = self.resource['id']
        arglist = [target, '--name', 'my-name']
        verifylist = [(self.res, target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)

    def test_set_no_destination_fwg(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-destination-firewall-group',
        ]
        verifylist = [
            (self.res, target),
            ('no_destination_firewall_group', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_firewall_group_id': None})
        self.assertIsNone(result)

    def test_set_no_source_fwg(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-source-firewall-group',
        ]
        verifylist = [
            (self.res, target),
            ('no_source_firewall_group', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_firewall_group_id': None})
        self.assertIsNone(result)

    def test_create_with_src_fwg_and_no(self):
        target = self.resource['id']
        fwg = 'my-fwg'
        arglist = [
            target,
            '--source-firewall-group', fwg,
            '--no-source-firewall-group',
        ]
        verifylist = [
            (self.res, target),
            ('source_firewall_group', fwg),
            ('no_source_firewall_group', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_dst_fwg_and_no(self):
        target = self.resource['id']
        fwg = 'my-fwg'
        arglist = [
            target,
            '--destination-firewall-group', fwg,
            '--no-destination-firewall-group',
        ]
        verifylist = [
            (self.res, target),
            ('destination_firewall_group', fwg),
            ('no_destination_firewall_group', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestUnsetFirewallRule(TestFirewallRule, common.TestUnsetFWaaS):

    def setUp(self):
        super(TestUnsetFirewallRule, self).setUp()
        self.networkclient.update_firewall_rule = mock.Mock(
            return_value={self.res: _fwr})
        self.mocked = self.networkclient.update_firewall_rule

        def _mock_find_rule(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = firewallrule.UnsetFirewallRule(self.app, self.namespace)

    def test_unset_protocol_and_raise(self):
        self.networkclient.update_firewall_rule.side_effect = Exception
        target = self.resource['id']
        arglist = [
            target,
            '--protocol',
        ]
        verifylist = [
            (self.res, target),
            ('protocol', False)
        ]
        self.assertRaises(utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_unset_source_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-port',
        ]
        verifylist = [
            (self.res, target),
            ('source_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_port': None})
        self.assertIsNone(result)

    def test_unset_destination_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-port',
        ]
        verifylist = [
            (self.res, target),
            ('destination_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_port': None})
        self.assertIsNone(result)

    def test_unset_source_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('source_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_ip_address': None})
        self.assertIsNone(result)

    def test_unset_destination_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('destination_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_ip_address': None})
        self.assertIsNone(result)

    def test_unset_enable_rule(self):
        target = self.resource['id']
        arglist = [
            target,
            '--enable-rule',
        ]
        verifylist = [
            (self.res, target),
            ('enable_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'enabled': False})
        self.assertIsNone(result)


class TestDeleteFirewallRule(TestFirewallRule, common.TestDeleteFWaaS):

    def setUp(self):
        super(TestDeleteFirewallRule, self).setUp()
        self.networkclient.delete_firewall_rule = mock.Mock(return_value=_fwr)
        self.mocked = self.networkclient.delete_firewall_rule
        self.cmd = firewallrule.DeleteFirewallRule(self.app, self.namespace)
