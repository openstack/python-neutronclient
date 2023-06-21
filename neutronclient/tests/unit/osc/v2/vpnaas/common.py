# Copyright 2017 FUJITSU LIMITED
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

from neutronclient.tests.unit.osc.v2 import fakes as test_fakes


class TestCreateVPNaaS(test_fakes.TestNeutronClientOSCV2):
    pass


class TestDeleteVPNaaS(test_fakes.TestNeutronClientOSCV2):

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_vpnaas(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_vpn_endpoint_group.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_ipsec_site_connection.side_effect = \
            _mock_vpnaas
        self.networkclient.find_vpn_ike_policy.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_ipsec_policy.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_service.side_effect = _mock_vpnaas

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_vpnaas(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_vpn_endpoint_group.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_ipsec_site_connection.side_effect = \
            _mock_vpnaas
        self.networkclient.find_vpn_ike_policy.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_ipsec_policy.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_service.side_effect = _mock_vpnaas

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

    def test_delete_multiple_with_exception(self):
        target1 = 'target'
        arglist = [target1]
        verifylist = [(self.res, [target1])]

        self.networkclient.find_vpn_ipsec_site_connection.side_effect = [
            target1, exceptions.CommandError
        ]
        self.networkclient.find_vpn_endpoint_group.side_effect = [
            target1, exceptions.CommandError
        ]
        self.networkclient.find_vpn_ike_policy.side_effect = [
            target1, exceptions.CommandError
        ]
        self.networkclient.find_vpn_service.side_effect = [
            target1, exceptions.CommandError
        ]
        self.networkclient.find_vpn_ipsec_policy.side_effect = [
            target1, exceptions.CommandError
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        resource_name = self.res.replace('_', ' ')
        msg = "1 of 2 %s(s) failed to delete." % resource_name
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestListVPNaaS(test_fakes.TestNeutronClientOSCV2):

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


class TestSetVPNaaS(test_fakes.TestNeutronClientOSCV2):

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
            target, **{'name': update})
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
            target, **{'description': update})
        self.assertIsNone(result)


class TestShowVPNaaS(test_fakes.TestNeutronClientOSCV2):

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        def _mock_vpnaas(*args, **kwargs):
            return {'id': args[0]}

        self.networkclient.find_vpn_endpoint_group.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_ipsec_site_connection.side_effect = \
            _mock_vpnaas
        self.networkclient.find_vpn_ike_policy.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_ipsec_policy.side_effect = _mock_vpnaas
        self.networkclient.find_vpn_service.side_effect = _mock_vpnaas

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)
        self.assertItemEqual(self.ordered_data, data)
