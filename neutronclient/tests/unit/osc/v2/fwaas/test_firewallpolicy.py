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

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.fwaas import firewallpolicy
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.fwaas import common
from neutronclient.tests.unit.osc.v2.fwaas import fakes


_fwp = fakes.FirewallPolicy().create()
CONVERT_MAP = {
    'share': 'shared',
    'no_share': 'shared',
    'project': 'tenant_id',
    'port': 'ports',
    'name': 'name',
    'id': 'id',
    'firewall_rule': 'firewall_rules',
    'description': 'description'
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _fwp
    if data:
        source.update(data)
    return tuple(source[key] for key in source)


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = _fwp
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        if re.match('^no_', key) and val is True:
            new_value = None
        elif key == 'enable' and val:
            new_value = True
        elif key == 'disable' and val:
            new_value = False
        elif val is True or val is False:
            new_value = val
        elif key in ('name', 'description'):
            new_value = val
        else:
            new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestFirewallPolicy(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))

    def setUp(self):
        super(TestFirewallPolicy, self).setUp()

        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _fwp['tenant_id']
        self.res = 'firewall_policy'
        self.res_plural = 'firewall_policies'
        self.resource = _fwp
        self.list_headers = (
            'ID',
            'Name',
            'Firewall Rules',
        )
        self.list_data = (
            _fwp['id'],
            _fwp['name'],
            _fwp['firewall_rules'],
        )
        self.headers = tuple(self.list_headers + (
            'Description',
            'Audited',
            'Shared',
            'Project')
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Audited',
            'Description',
            'Firewall Rules',
            'ID',
            'Name',
            'Project',
            'Shared',
        )
        self.ordered_data = (
            _fwp['audited'],
            _fwp['description'],
            _fwp['firewall_rules'],
            _fwp['id'],
            _fwp['name'],
            _fwp['tenant_id'],
            _fwp['shared'],
        )
        self.ordered_columns = (
            'audited',
            'description',
            'firewall_rules',
            'id',
            'name',
            'tenant_id',
            'shared',
        )


class TestCreateFirewallPolicy(TestFirewallPolicy, common.TestCreateFWaaS):

    def setUp(self):
        super(TestCreateFirewallPolicy, self).setUp()
        self.networkclient.create_firewall_policy = mock.Mock(
            return_value={self.res: _fwp})
        self.mocked = self.networkclient.create_firewall_policy
        self.cmd = firewallpolicy.CreateFirewallPolicy(self.app,
                                                       self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.networkclient.create_firewall_policy.return_value = response
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(data=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_mandatory_param(self):
        name = 'my-fwg'
        arglist = [
            name,
        ]
        verifylist = [
            ('name', name),
        ]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_rules(self):
        name = 'my-fwg'
        rule1 = 'rule1'
        rule2 = 'rule2'

        def _mock_policy(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_rule.side_effect = _mock_policy

        arglist = [
            name,
            '--firewall-rule', rule1,
            '--firewall-rule', rule2,
        ]
        verifylist = [
            ('name', name),
            ('firewall_rule', [rule1, rule2]),
        ]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.assertEqual(2, self.networkclient.find_firewall_rule.call_count)

        self.check_results(headers, data, request)

    def test_create_with_all_params(self):
        name = 'my-fwp'
        desc = 'my-desc'
        rule1 = 'rule1'
        rule2 = 'rule2'
        project = 'my-tenant'

        def _mock_find(*args, **kwargs):
            if self.res in args[0]:
                rules = _fwp['firewall_rules']
                return {'id': args[0], 'firewall_rules': rules}
            return {'id': args[0]}

        self.networkclient.find_firewall_policy.side_effect = _mock_find
        self.networkclient.find_firewall_rule.side_effect = _mock_find

        arglist = [
            name,
            '--description', desc,
            '--firewall-rule', rule1,
            '--firewall-rule', rule2,
            '--project', project,
            '--share',
            '--audited',
        ]
        verifylist = [
            ('name', name),
            ('description', desc),
            ('firewall_rule', [rule1, rule2]),
            ('project', project),
            ('share', True),
            ('audited', True),
        ]
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_firewall_rule_and_no(self):
        name = 'my-fwp'
        rule1 = 'rule1'
        rule2 = 'rule2'
        arglist = [
            name,
            '--firewall-rule', rule1,
            '--firewall-rule', rule2,
            '--no-firewall-rule',
        ]
        verifylist = [
            ('name', name),
            ('firewall_rule', [rule1, rule2]),
            ('no_firewall_rule', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_shared_and_no_share(self):
        name = 'my-fwp'
        arglist = [
            name,
            '--share',
            '--no-share',
        ]
        verifylist = [
            ('name', name),
            ('share', True),
            ('no_share', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_audited_and_no(self):
        name = 'my-fwp'
        arglist = [
            name,
            '--audited',
            '--no-audited',
        ]
        verifylist = [
            ('name', name),
            ('audited', True),
            ('no_audited', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestListFirewallPolicy(TestFirewallPolicy, common.TestListFWaaS):

    def setUp(self):
        super(TestListFirewallPolicy, self).setUp()
        self.networkclient.firewall_policies = mock.Mock(
            return_value=[_fwp])
        self.mocked = self.networkclient.firewall_policies
        self.cmd = firewallpolicy.ListFirewallPolicy(self.app, self.namespace)


class TestShowFirewallPolicy(TestFirewallPolicy, common.TestShowFWaaS):

    def setUp(self):
        super(TestShowFirewallPolicy, self).setUp()
        self.networkclient.get_firewall_policy = mock.Mock(
            return_value=_fwp)
        self.mocked = self.networkclient.get_firewall_policy
        self.cmd = firewallpolicy.ShowFirewallPolicy(self.app, self.namespace)


class TestSetFirewallPolicy(TestFirewallPolicy, common.TestSetFWaaS):

    def setUp(self):
        super(TestSetFirewallPolicy, self).setUp()
        self.networkclient.update_firewall_policy = mock.Mock(
            return_value=_fwp)
        self.mocked = self.networkclient.update_firewall_policy

        def _mock_find_rule(*args, **kwargs):
            return {'id': args[0]}

        def _mock_find_policy(*args, **kwargs):
            return {'id': args[0],
                    'firewall_rules': _fwp['firewall_rules']}

        self.networkclient.find_firewall_policy.side_effect = _mock_find_policy
        self.networkclient.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = firewallpolicy.SetFirewallPolicy(self.app, self.namespace)

    def test_set_rules(self):
        target = self.resource['id']
        rule1 = 'new_rule1'
        rule2 = 'new_rule2'
        arglist = [
            target,
            '--firewall-rule', rule1,
            '--firewall-rule', rule2,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule1, rule2]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        expect = _fwp['firewall_rules'] + [rule1, rule2]
        body = {'firewall_rules': expect}
        self.mocked.assert_called_once_with(target, **body)
        self.assertEqual(2, self.networkclient.find_firewall_rule.call_count)
        self.assertEqual(2, self.networkclient.find_firewall_policy.call_count)
        self.assertIsNone(result)

    def test_set_no_rules(self):
        target = self.resource['id']
        arglist = [target, '--no-firewall-rule']
        verifylist = [
            (self.res, target),
            ('no_firewall_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': []}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_set_rules_and_no_rules(self):
        target = self.resource['id']
        rule1 = 'rule1'
        arglist = [
            target,
            '--firewall-rule', rule1,
            '--no-firewall-rule',
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule1]),
            ('no_firewall_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': [rule1]}
        self.mocked.assert_called_once_with(target, **body)
        self.assertEqual(1, self.networkclient.find_firewall_rule.call_count)
        self.assertEqual(1, self.networkclient.find_firewall_policy.call_count)
        self.assertIsNone(result)

    def test_set_audited(self):
        target = self.resource['id']
        arglist = [target, '--audited']
        verifylist = [
            (self.res, target),
            ('audited', True),
        ]
        body = {'audited': True}
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_set_no_audited(self):
        target = self.resource['id']
        arglist = [target, '--no-audited']
        verifylist = [
            (self.res, target),
            ('no_audited', True),
        ]
        body = {'audited': False}
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_set_audited_and_no_audited(self):
        target = self.resource['id']
        arglist = [
            target,
            '--audited',
            '--no-audited',
        ]
        verifylist = [
            (self.res, target),
            ('audited', True),
            ('no_audited', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_and_raises(self):
        self.networkclient.update_firewall_policy = mock.Mock(
            side_effect=Exception)
        target = self.resource['id']

        arglist = [target, '--name', 'my-name']
        verifylist = [(self.res, target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


class TestDeleteFirewallPolicy(TestFirewallPolicy, common.TestDeleteFWaaS):

    def setUp(self):
        super(TestDeleteFirewallPolicy, self).setUp()
        self.networkclient.delete_firewall_policy = mock.Mock(
            return_value={self.res: _fwp})
        self.mocked = self.networkclient.delete_firewall_policy
        self.cmd = firewallpolicy.DeleteFirewallPolicy(
            self.app, self.namespace)


class TestFirewallPolicyInsertRule(TestFirewallPolicy):

    def setUp(self):
        super(TestFirewallPolicyInsertRule, self).setUp()
        self.networkclient.insert_rule_firewall_policy = mock.Mock(
            return_value={self.res: _fwp})
        self.mocked = self.networkclient.insert_rule_into_policy

        def _mock_find_policy(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_policy.side_effect = _mock_find_policy
        self.networkclient.find_firewall_rule.side_effect = _mock_find_policy

        self.cmd = firewallpolicy.FirewallPolicyInsertRule(self.app,
                                                           self.namespace)

    def test_insert_firewall_rule(self):
        target = self.resource['id']
        rule = 'new-rule'
        before = 'before'
        after = 'after'
        arglist = [
            target,
            rule,
            '--insert-before', before,
            '--insert-after', after,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', rule),
            ('insert_before', before),
            ('insert_after', after),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {
            'firewall_rule_id': rule,
            'insert_before': before,
            'insert_after': after
        }
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
        self.assertEqual(1, self.networkclient.find_firewall_policy.call_count)
        self.assertEqual(3, self.networkclient.find_firewall_rule.call_count)

    def test_insert_with_no_firewall_rule(self):
        target = self.resource['id']
        arglist = [
            target,
        ]
        verifylist = [
            (self.res, target),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestFirewallPolicyRemoveRule(TestFirewallPolicy):

    def setUp(self):
        super(TestFirewallPolicyRemoveRule, self).setUp()
        self.networkclient.remove_rule_firewall_policy = mock.Mock(
            return_value={self.res: _fwp})
        self.mocked = self.networkclient.remove_rule_from_policy

        def _mock_find_policy(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_policy.side_effect = _mock_find_policy
        self.networkclient.find_firewall_rule.side_effect = _mock_find_policy

        self.cmd = firewallpolicy.FirewallPolicyRemoveRule(self.app,
                                                           self.namespace)

    def test_remove_firewall_rule(self):
        target = self.resource['id']
        rule = 'remove-rule'
        arglist = [
            target,
            rule,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', rule),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        body = {'firewall_rule_id': rule}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
        self.assertEqual(1, self.networkclient.find_firewall_policy.call_count)
        self.assertEqual(1, self.networkclient.find_firewall_rule.call_count)

    def test_remove_with_no_firewall_rule(self):
        target = self.resource['id']
        arglist = [
            target,
        ]
        verifylist = [
            (self.res, target),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestUnsetFirewallPolicy(TestFirewallPolicy, common.TestUnsetFWaaS):

    def setUp(self):
        super(TestUnsetFirewallPolicy, self).setUp()
        self.networkclient.update_firewall_policy = mock.Mock(
            return_value={self.res: _fwp})
        self.mocked = self.networkclient.update_firewall_policy

        def _mock_find_rule(*args, **kwargs):
            return {'id': args[0]}

        def _mock_find_policy(*args, **kwargs):
            return {'id': args[0], 'firewall_rules': _fwp['firewall_rules']}

        self.networkclient.find_firewall_policy.side_effect = _mock_find_policy
        self.networkclient.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = firewallpolicy.UnsetFirewallPolicy(self.app, self.namespace)

    def test_unset_audited(self):
        target = self.resource['id']
        arglist = [
            target,
            '--audited',
        ]
        verifylist = [
            (self.res, target),
            ('audited', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'audited': False}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_unset_firewall_rule_not_matched(self):
        _fwp['firewall_rules'] = ['old_rule']
        target = self.resource['id']
        rule = 'new_rule'
        arglist = [
            target,
            '--firewall-rule', rule,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': _fwp['firewall_rules']}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_unset_firewall_rule_matched(self):
        _fwp['firewall_rules'] = ['rule1', 'rule2']
        target = self.resource['id']
        rule = 'rule1'
        arglist = [
            target,
            '--firewall-rule', rule,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': ['rule2']}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
        self.assertEqual(2, self.networkclient.find_firewall_policy.call_count)
        self.assertEqual(1, self.networkclient.find_firewall_rule.call_count)

    def test_unset_all_firewall_rule(self):
        target = self.resource['id']
        arglist = [
            target,
            '--all-firewall-rule',
        ]
        verifylist = [
            (self.res, target),
            ('all_firewall_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': []}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
