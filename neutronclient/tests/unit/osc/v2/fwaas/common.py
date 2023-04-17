# Copyright 2016-2017 FUJITSU LIMITED
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

import testtools

from osc_lib import exceptions
from osc_lib.tests import utils

from neutronclient.tests.unit.osc.v2 import fakes as test_fakes


class TestListFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.list_headers), headers)
        self.assertEqual([self.list_data], list(data))

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)


class TestShowFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']
        headers, data = None, None

        def _mock_fwaas(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_policy.side_effect = _mock_fwaas
        self.networkclient.find_firewall_group.side_effect = _mock_fwaas
        self.networkclient.find_firewall_rule.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)


class TestCreateFWaaS(test_fakes.TestNeutronClientOSCV2):
    pass


class TestSetFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_set_name(self):
        target = self.resource['id']
        update = 'change'
        arglist = [target, '--name', update]
        verifylist = [
            (self.res, target),
            ('name', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'name': update})
        self.assertIsNone(result)

    def test_set_description(self):
        target = self.resource['id']
        update = 'change-desc'
        arglist = [target, '--description', update]
        verifylist = [
            (self.res, target),
            ('description', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'description': update})
        self.assertIsNone(result)

    def test_set_shared(self):
        target = self.resource['id']
        arglist = [target, '--share']
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': True})
        self.assertIsNone(result)

    def test_set_duplicate_shared(self):
        target = self.resource['id']
        arglist = [target, '--share', '--share']
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': True})
        self.assertIsNone(result)

    def test_set_no_share(self):
        target = self.resource['id']
        arglist = [target, '--no-share']
        verifylist = [
            (self.res, target),
            ('share', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_set_duplicate_no_share(self):
        target = self.resource['id']
        arglist = [target, '--no-share', '--no-share']
        verifylist = [
            (self.res, target),
            ('no_share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_set_no_share_and_shared(self):
        target = self.resource['id']
        arglist = [target, '--no-share', '--share']
        verifylist = [
            (self.res, target),
            ('no_share', True),
            ('share', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_shared_and_no_share(self):
        target = self.resource['id']
        arglist = [target, '--share', '--no_share']
        verifylist = [
            (self.res, target),
            ('share', True),
            ('no_share', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_project(self):
        target = self.resource['id']
        project_id = 'b14ce3b699594d13819a859480286489'
        arglist = [target, '--project', project_id]
        verifylist = [
            (self.res, target),
            ('tenant_id', project_id),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_project_domain(self):
        target = self.resource['id']
        project_domain = 'mydomain.com'
        arglist = [target, '--project-domain', project_domain]
        verifylist = [
            (self.res, target),
            ('project_domain', project_domain),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)


class TestDeleteFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_group.side_effect = _mock_fwaas
        self.networkclient.find_firewall_policy.side_effect = _mock_fwaas
        self.networkclient.find_firewall_rule.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_fwaas(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_firewall_group.side_effect = _mock_fwaas
        self.networkclient.find_firewall_policy.side_effect = _mock_fwaas
        self.networkclient.find_firewall_rule.side_effect = _mock_fwaas

        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0][0])
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        target1 = 'target'
        arglist = [target1]
        verifylist = [(self.res, [target1])]

        self.networkclient.find_firewall_group.side_effect = [
            target1, exceptions.CommandError
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        resource_name = self.res.replace('_', ' ')
        msg = "1 of 2 %s(s) failed to delete." % resource_name
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestUnsetFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_unset_shared(self):
        target = self.resource['id']
        arglist = [
            target,
            '--share',
        ]
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_set_shared_and_no_shared(self):
        target = self.resource['id']
        arglist = [target, '--share', '--no-share']
        verifylist = [
            (self.res, target),
            ('share', True),
            ('no_share', True),
        ]
        # check_parser: error: unrecognized arguments: --no-share
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_duplicate_shared(self):
        target = self.resource['id']
        arglist = [target, '--share', '--share']
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)
