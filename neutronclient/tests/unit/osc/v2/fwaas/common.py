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
        self.assertEqual([self.data], list(data))


class TestShowFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']
        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)


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

        self.mocked.assert_called_once_with(
            target, {self.res: {'name': update}})
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

        self.mocked.assert_called_once_with(
            target, {self.res: {'description': update}})
        self.assertIsNone(result)

    def test_set_public(self):
        target = self.resource['id']
        arglist = [target, '--public']
        verifylist = [
            (self.res, target),
            ('public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'public': True}})
        self.assertIsNone(result)

    def test_set_duplicate_public(self):
        target = self.resource['id']
        arglist = [target, '--public', '--public']
        verifylist = [
            (self.res, target),
            ('public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'public': True}})
        self.assertIsNone(result)

    def test_set_private(self):
        target = self.resource['id']
        arglist = [target, '--private']
        verifylist = [
            (self.res, target),
            ('public', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'public': False}})
        self.assertIsNone(result)

    def test_set_duplicate_private(self):
        target = self.resource['id']
        arglist = [target, '--private', '--private']
        verifylist = [
            (self.res, target),
            ('public', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'public': False}})
        self.assertIsNone(result)

    def test_set_private_and_public(self):
        target = self.resource['id']
        arglist = [target, '--private', '--public']
        verifylist = [
            (self.res, target),
            ('private', True),
            ('public', True),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_public_and_priavte(self):
        target = self.resource['id']
        arglist = [target, '--public', '--private']
        verifylist = [
            (self.res, target),
            ('public', True),
            ('private', True),
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
        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):
        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0])
            self.assertEqual(reference, actual)


class TestUnsetFWaaS(test_fakes.TestNeutronClientOSCV2):

    def test_unset_public(self):
        target = self.resource['id']
        arglist = [
            target,
            '--public',
        ]
        verifylist = [
            (self.res, target),
            ('public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, {self.res: {'public': False}})
        self.assertIsNone(result)

    def test_set_public_and_priavte(self):
        target = self.resource['id']
        arglist = [target, '--public', '--private']
        verifylist = [
            (self.res, target),
            ('public', True),
            ('private', True),
        ]
        # check_parser: error: unrecognized arguments: --private
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_set_duplicate_public(self):
        target = self.resource['id']
        arglist = [target, '--public', '--public']
        verifylist = [
            (self.res, target),
            ('public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'public': False}})
        self.assertIsNone(result)
