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

import copy
import re

import mock
from osc_lib import exceptions
from osc_lib.tests import utils

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.fwaas import constants as const
from neutronclient.osc.v2.fwaas import firewallgroup
from neutronclient.osc.v2 import utils as v2_utils
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.fwaas import common
from neutronclient.tests.unit.osc.v2.fwaas import fakes


_fwg = fakes.FirewallGroup().create()
CONVERT_MAP = {
    'ingress_firewall_policy': 'ingress_firewall_policy_id',
    'egress_firewall_policy': 'egress_firewall_policy_id',
    'no_ingress_firewall_policy': 'ingress_firewall_policy_id',
    'no_egress_firewall_policy': 'egress_firewall_policy_id',
    'share': 'shared',
    'no_share': 'shared',
    'project': 'tenant_id',
    'enable': 'admin_state_up',
    'disable': 'admin_state_up',
    'port': 'ports',
}


def _generate_response(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _fwg
    up = {'admin_state_up':
          v2_utils.AdminStateColumn(source['admin_state_up'])}
    if data:
        up.append(data)
    source.update(up)
    return tuple(source[key] for key in source)


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = copy.deepcopy(_fwg)
    for key, val in verifylist:
        del request[key]
        if re.match('^no_', key) and val is True:
            new_value = None
        elif key == 'enable' and val:
            new_value = True
        elif key == 'disable' and val:
            new_value = False
        else:
            new_value = val
        converted = CONVERT_MAP.get(key, key)
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestFirewallGroup(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = {self.res: exp_req}
        self.mocked.assert_called_once_with(req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertItemEqual(self.ordered_data, data)

    def setUp(self):
        super(TestFirewallGroup, self).setUp()

        def _find_resource(*args, **kwargs):
            return {'id': args[1], 'ports': _fwg['ports']}

        self.neutronclient.find_resource = mock.Mock(
            side_effect=_find_resource)
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _fwg['tenant_id']
        self.res = 'firewall_group'
        self.res_plural = 'firewall_groups'
        self.resource = _fwg
        self.list_headers = (
            'ID',
            'Name',
            'Ingress Policy ID',
            'Egress Policy ID',
        )
        self.list_data = (
            _fwg['id'],
            _fwg['name'],
            _fwg['ingress_firewall_policy_id'],
            _fwg['egress_firewall_policy_id'],
        )
        self.headers = tuple(self.list_headers + (
            'Description',
            'Status',
            'Ports',
            'State',
            'Shared',
            'Project',
        ))
        self.data = _generate_response()
        self.ordered_headers = copy.deepcopy(tuple(sorted(self.headers)))
        self.ordered_data = (
            _fwg['description'],
            _fwg['egress_firewall_policy_id'],
            _fwg['id'],
            _fwg['ingress_firewall_policy_id'],
            _fwg['name'],
            _fwg['ports'],
            _fwg['tenant_id'],
            _fwg['shared'],
            v2_utils.AdminStateColumn(_fwg['admin_state_up']),
            _fwg['status'],
        )
        self.ordered_columns = (
            'description',
            'egress_firewall_policy_id',
            'id',
            'ingress_firewall_policy_id',
            'name',
            'ports',
            'tenant_id',
            'shared',
            'admin_state_up',
            'status',
        )


class TestCreateFirewallGroup(TestFirewallGroup, common.TestCreateFWaaS):

    def setUp(self):
        # Mock objects
        super(TestCreateFirewallGroup, self).setUp()
        self.neutronclient.create_fwaas_firewall_group = mock.Mock(
            return_value={self.res: _fwg})
        self.mocked = self.neutronclient.create_fwaas_firewall_group
        self.cmd = firewallgroup.CreateFirewallGroup(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.neutronclient.create_fwaas_firewall_group.return_value = \
            {self.res: dict(response)}
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_response(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def test_create_with_no_option(self):
        # firewall_group-create with mandatory (none) params.
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.ordered_headers, headers)
        self.assertItemEqual(self.ordered_data, data)

    def test_create_with_port(self):
        # firewall_group-create with 'port'
        port_id = 'id_for_port'
        arglist = ['--port', port_id]
        verifylist = [('port', [port_id])]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_ingress_policy(self):
        ingress_policy = 'my-ingress-policy'

        def _mock_port_fwg(*args, **kwargs):
            return {'id': args[1]}

        self.neutronclient.find_resource.side_effect = _mock_port_fwg

        arglist = ['--ingress-firewall-policy', ingress_policy]
        verifylist = [('ingress_firewall_policy', ingress_policy)]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.neutronclient.find_resource.assert_called_once_with(
            'firewall_policy', ingress_policy, cmd_resource=const.CMD_FWP)

        self.check_results(headers, data, request)

    def test_create_with_egress_policy(self):
        egress_policy = 'my-egress-policy'

        def _mock_port_fwg(*args, **kwargs):
            return {'id': args[1]}

        self.neutronclient.find_resource.side_effect = _mock_port_fwg

        arglist = ['--egress-firewall-policy', egress_policy]
        verifylist = [('egress_firewall_policy', egress_policy)]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.neutronclient.find_resource.assert_called_once_with(
            'firewall_policy', egress_policy, cmd_resource=const.CMD_FWP)
        self.check_results(headers, data, request)

    def test_create_with_all_params(self):
        name = 'my-name'
        description = 'my-desc'
        ingress_policy = 'my-ingress-policy'
        egress_policy = 'my-egress-policy'
        port = 'port'
        tenant_id = 'my-tenant'
        arglist = [
            '--name', name,
            '--description', description,
            '--ingress-firewall-policy', ingress_policy,
            '--egress-firewall-policy', egress_policy,
            '--port', port,
            '--project', tenant_id,
            '--share',
            '--disable',
        ]
        verifylist = [
            ('name', name),
            ('description', description),
            ('ingress_firewall_policy', ingress_policy),
            ('egress_firewall_policy', egress_policy),
            ('port', [port]),
            ('share', True),
            ('project', tenant_id),
            ('disable', True),
        ]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_shared_and_no_share(self):
        arglist = [
            '--share',
            '--no-share',
        ]
        verifylist = [
            ('share', True),
            ('no_share', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_ports_and_no(self):
        port = 'my-port'
        arglist = [
            '--port', port,
            '--no-port',
        ]
        verifylist = [
            ('port', [port]),
            ('no_port', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_ingress_policy_and_no(self):
        policy = 'my-policy'
        arglist = [
            '--ingress-firewall-policy', policy,
            '--no-ingress-firewall-policy',
        ]
        verifylist = [
            ('ingress_firewall_policy', policy),
            ('no_ingress_firewall_policy', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_egress_policy_and_no(self):
        policy = 'my-policy'
        arglist = [
            '--egress-firewall-policy', policy,
            '--no-egress-firewall-policy',
        ]
        verifylist = [
            ('egress_firewall_policy', policy),
            ('no_egress_firewall_policy', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestListFirewallGroup(TestFirewallGroup, common.TestListFWaaS):

    def setUp(self):
        super(TestListFirewallGroup, self).setUp()
        # Mock objects
        self.neutronclient.list_fwaas_firewall_groups = mock.Mock(
            return_value={self.res_plural: [_fwg]})
        self.mocked = self.neutronclient.list_fwaas_firewall_groups
        self.cmd = firewallgroup.ListFirewallGroup(self.app, self.namespace)


class TestShowFirewallGroup(TestFirewallGroup, common.TestShowFWaaS):

    def setUp(self):
        super(TestShowFirewallGroup, self).setUp()
        # Mock objects
        self.neutronclient.show_fwaas_firewall_group = mock.Mock(
            return_value={self.res: _fwg})
        self.mocked = self.neutronclient.show_fwaas_firewall_group
        self.cmd = firewallgroup.ShowFirewallGroup(self.app, self.namespace)


class TestSetFirewallGroup(TestFirewallGroup, common.TestSetFWaaS):

    def setUp(self):
        super(TestSetFirewallGroup, self).setUp()
        # Mock objects
        _fwg['ports'] = ['old_port']
        self.neutronclient.update_fwaas_firewall_group = mock.Mock(
            return_value={self.res: _fwg})
        self.mocked = self.neutronclient.update_fwaas_firewall_group
        self.cmd = firewallgroup.SetFirewallGroup(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_response(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def test_set_ingress_policy_and_egress_policy(self):
        target = self.resource['id']
        ingress_policy = 'ingress_policy'
        egress_policy = 'egress_policy'

        def _mock_fwg_policy(*args, **kwargs):
            # 1. Find specified firewall_group
            if self.neutronclient.find_resource.call_count == 1:
                self.neutronclient.find_resource.assert_called_with(
                    self.res, target, cmd_resource=const.CMD_FWG)
            # 2. Find specified 'ingress_firewall_policy'
            if self.neutronclient.find_resource.call_count == 2:
                self.neutronclient.find_resource.assert_called_with(
                    'firewall_policy', ingress_policy,
                    cmd_resource=const.CMD_FWP)
            # 3. Find specified 'ingress_firewall_policy'
            if self.neutronclient.find_resource.call_count == 3:
                self.neutronclient.find_resource.assert_called_with(
                    'firewall_policy', egress_policy,
                    cmd_resource=const.CMD_FWP)
            return {'id': args[1]}

        self.neutronclient.find_resource.side_effect = _mock_fwg_policy

        arglist = [
            target,
            '--ingress-firewall-policy', ingress_policy,
            '--egress-firewall-policy', egress_policy,
        ]
        verifylist = [
            (self.res, target),
            ('ingress_firewall_policy', ingress_policy),
            ('egress_firewall_policy', egress_policy),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'ingress_firewall_policy_id': ingress_policy,
                                'egress_firewall_policy_id': egress_policy}})
        self.assertIsNone(result)

    def test_set_port(self):
        target = self.resource['id']
        port1 = 'additional_port1'
        port2 = 'additional_port2'

        def _mock_port_fwg(*args, **kwargs):
            # 1. Find specified firewall_group
            if self.neutronclient.find_resource.call_count == 1:
                self.neutronclient.find_resource.assert_called_with(
                    self.res, target, cmd_resource=const.CMD_FWG)
                return {'id': args[1]}
            # 2. Find specified 'port' #1
            if self.neutronclient.find_resource.call_count == 2:
                self.neutronclient.find_resource.assert_called_with(
                    'port', args[1])
                return {'id': args[1]}
            # 3. Find specified 'port' #2
            if self.neutronclient.find_resource.call_count == 3:
                self.neutronclient.find_resource.assert_called_with(
                    'port', args[1])
                return {'id': args[1]}
            # 4. Find specified firewall_group and refer 'ports' attribute
            if self.neutronclient.find_resource.call_count == 4:
                self.neutronclient.find_resource.assert_called_with(
                    self.res, target, cmd_resource=const.CMD_FWG)
                return {'ports': _fwg['ports']}

        self.neutronclient.find_resource.side_effect = _mock_port_fwg

        arglist = [
            target,
            '--port', port1,
            '--port', port2,
        ]
        verifylist = [
            (self.res, target),
            ('port', [port1, port2]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        expect = {'ports': sorted(_fwg['ports'] + [port1, port2])}
        self.mocked.assert_called_once_with(target, {self.res: expect})
        self.assertEqual(4, self.neutronclient.find_resource.call_count)
        self.assertIsNone(result)

    def test_set_no_port(self):
        # firewall_group-update myid --policy newpolicy.
        target = self.resource['id']
        arglist = [target, '--no-port']
        verifylist = [
            (self.res, target),
            ('no_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'ports': []}})
        self.assertIsNone(result)

    def test_set_admin_state(self):
        target = self.resource['id']
        arglist = [target, '--enable']
        verifylist = [
            (self.res, target),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'admin_state_up': True}})
        self.assertIsNone(result)

    def test_set_egress_policy(self):
        target = self.resource['id']
        policy = 'egress_policy'
        arglist = [target, '--egress-firewall-policy', policy]
        verifylist = [
            (self.res, target),
            ('egress_firewall_policy', policy),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'egress_firewall_policy_id': policy}})
        self.assertIsNone(result)

    def test_set_no_ingress_policies(self):
        target = self.resource['id']
        arglist = [target, '--no-ingress-firewall-policy']
        verifylist = [
            (self.res, target),
            ('no_ingress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'ingress_firewall_policy_id': None}})
        self.assertIsNone(result)

    def test_set_no_egress_policies(self):
        target = self.resource['id']
        arglist = [target, '--no-egress-firewall-policy']
        verifylist = [
            (self.res, target),
            ('no_egress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'egress_firewall_policy_id': None}})
        self.assertIsNone(result)

    def test_set_port_and_no_port(self):
        target = self.resource['id']
        port = 'my-port'
        arglist = [
            target,
            '--port', port,
            '--no-port',
        ]
        verifylist = [
            (self.res, target),
            ('port', [port]),
            ('no_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, {self.res: {'ports': [port]}})
        self.assertIsNone(result)

    def test_set_ingress_policy_and_no_ingress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--ingress-firewall-policy', 'my-ingress',
            '--no-ingress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('ingress_firewall_policy', 'my-ingress'),
            ('no_ingress_firewall_policy', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_egress_policy_and_no_egress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--egress-firewall-policy', 'my-egress',
            '--no-egress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('egress_firewall_policy', 'my-egress'),
            ('no_egress_firewall_policy', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_and_raises(self):
        self.neutronclient.update_fwaas_firewall_group = mock.Mock(
            side_effect=Exception)
        target = self.resource['id']
        arglist = [target, '--name', 'my-name']
        verifylist = [(self.res, target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


class TestDeleteFirewallGroup(TestFirewallGroup, common.TestDeleteFWaaS):

    def setUp(self):
        super(TestDeleteFirewallGroup, self).setUp()
        # Mock objects
        self.neutronclient.delete_fwaas_firewall_group = mock.Mock()
        self.mocked = self.neutronclient.delete_fwaas_firewall_group
        self.cmd = firewallgroup.DeleteFirewallGroup(self.app, self.namespace)


class TestUnsetFirewallGroup(TestFirewallGroup, common.TestUnsetFWaaS):

    def setUp(self):
        super(TestUnsetFirewallGroup, self).setUp()
        _fwg['ports'] = ['old_port']
        # Mock objects
        self.neutronclient.update_fwaas_firewall_group = mock.Mock()
        self.mocked = self.neutronclient.update_fwaas_firewall_group
        self.cmd = firewallgroup.UnsetFirewallGroup(self.app, self.namespace)

    def test_unset_ingress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--ingress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('ingress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, {self.res: {'ingress_firewall_policy_id': None}})
        self.assertIsNone(result)

    def test_unset_egress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--egress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('egress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, {self.res: {'egress_firewall_policy_id': None}})
        self.assertIsNone(result)

    def test_unset_enable(self):
        target = self.resource['id']
        arglist = [
            target,
            '--enable',
        ]
        verifylist = [
            (self.res, target),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, {self.res: {'admin_state_up': False}})
        self.assertIsNone(result)

    def test_unset_port(self):
        target = self.resource['id']
        port = 'old_port'

        def _mock_port_fwg(*args, **kwargs):
            # 1. Find specified firewall_group
            if self.neutronclient.find_resource.call_count == 1:
                self.neutronclient.find_resource.assert_called_with(
                    self.res, target, cmd_resource=const.CMD_FWG)
                return {'id': args[1]}
            # 2. Find specified firewall_group and refer 'ports' attribute
            if self.neutronclient.find_resource.call_count == 2:
                self.neutronclient.find_resource.assert_called_with(
                    self.res, target, cmd_resource=const.CMD_FWG)
                return {'ports': _fwg['ports']}
            # 3. Find specified 'port'
            if self.neutronclient.find_resource.call_count == 3:
                self.neutronclient.find_resource.assert_called_with(
                    'port', port)
                return {'id': args[1]}

        self.neutronclient.find_resource.side_effect = mock.Mock(
            side_effect=_mock_port_fwg)

        arglist = [
            target,
            '--port', port,
        ]
        verifylist = [
            (self.res, target),
            ('port', [port]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, {self.res: {'ports': []}})
        self.assertIsNone(result)

    def test_unset_all_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--all-port',
        ]
        verifylist = [
            (self.res, target),
            ('all_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, {self.res: {'ports': []}})
        self.assertIsNone(result)
