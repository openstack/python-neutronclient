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

from unittest import mock
import uuid


from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.vpnaas import vpnservice
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.vpnaas import common
from neutronclient.tests.unit.osc.v2.vpnaas import fakes


_vpnservice = fakes.VPNService().create()
CONVERT_MAP = {
    'project': 'project_id',
    'router': 'router_id',
    'subnet': 'subnet_id'
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _vpnservice
    if data:
        source.update(data)
    return source


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = _vpnservice
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestVPNService(test_fakes.TestNeutronClientOSCV2):

    def _check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: list(exp_req)}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super(TestVPNService, self).setUp()

        def _mock_vpnservice(*args, **kwargs):
            self.networkclient.find_vpn_service.assert_called_once_with(
                self.resource['id'], ignore_missing=False)
            return {'id': args[0]}

        self.networkclient.find_router = mock.Mock()
        self.networkclient.find_subnet = mock.Mock()
        self.fake_router = mock.Mock()
        self.fake_subnet = mock.Mock()
        self.networkclient.find_router.return_value = self.fake_router
        self.networkclient.find_subnet.return_value = self.fake_subnet
        self.args = {
            'name': 'my-name',
            'description': 'my-desc',
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'router_id': 'router-id-' + uuid.uuid4().hex,
            'subnet_id': 'subnet-id-' + uuid.uuid4().hex,

        }
        self.fake_subnet.id = self.args['subnet_id']
        self.fake_router.id = self.args['router_id']

        self.networkclient.find_vpn_service.side_effect = mock.Mock(
            side_effect=_mock_vpnservice)
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _vpnservice['project_id']

        self.res = 'vpnservice'
        self.res_plural = 'vpnservices'
        self.resource = _vpnservice
        self.headers = (
            'ID',
            'Name',
            'Router',
            'Subnet',
            'Flavor',
            'State',
            'Status',
            'Description',
            'Project',
            'Ext v4 IP',
            'Ext v6 IP',
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Description',
            'Ext v4 IP',
            'Ext v6 IP',
            'Flavor',
            'ID',
            'Name',
            'Project',
            'Router',
            'State',
            'Status',
            'Subnet',
        )
        self.ordered_data = (
            _vpnservice['description'],
            _vpnservice['external_v4_ip'],
            _vpnservice['external_v6_ip'],
            _vpnservice['flavor_id'],
            _vpnservice['id'],
            _vpnservice['name'],
            _vpnservice['project_id'],
            _vpnservice['router_id'],
            _vpnservice['admin_state_up'],
            _vpnservice['status'],
            _vpnservice['subnet_id'],
        )
        self.ordered_columns = (
            'description',
            'external_v4_ip',
            'external_v6_ip',
            'flavor_id',
            'id',
            'name',
            'project_id',
            'router_id',
            'admin_state_up',
            'status',
            'subnet_id',
        )


class TestCreateVPNService(TestVPNService, common.TestCreateVPNaaS):

    def setUp(self):
        super(TestCreateVPNService, self).setUp()
        self.networkclient.create_vpn_service = mock.Mock(
            return_value=_vpnservice)
        self.mocked = self.networkclient.create_vpn_service
        self.cmd = vpnservice.CreateVPNService(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.networkclient.create_vpn_service.return_value = response
        osc_utils.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self):
        name = self.args.get('name')
        description = self.args.get('description')
        router_id = self.args.get('router_id')
        subnet_id = self.args.get('subnet_id')
        project_id = self.args.get('project_id')
        arglist = [
            '--description', description,
            '--project', project_id,
            '--subnet', subnet_id,
            '--router', router_id,
            name,
        ]
        verifylist = [
            ('description', description),
            ('project', project_id),
            ('subnet', subnet_id),
            ('router', router_id),
            ('name', name),
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self):
        arglist, verifylist = self._set_all_params()
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self._check_results(headers, data, request)

    def test_create_with_all_params(self):
        self._test_create_with_all_params()


class TestDeleteVPNService(TestVPNService, common.TestDeleteVPNaaS):

    def setUp(self):
        super(TestDeleteVPNService, self).setUp()
        self.networkclient.delete_vpn_service = mock.Mock()
        self.mocked = self.networkclient.delete_vpn_service
        self.cmd = vpnservice.DeleteVPNService(self.app, self.namespace)


class TestListVPNService(TestVPNService):

    def setUp(self):
        super(TestListVPNService, self).setUp()
        self.cmd = vpnservice.ListVPNService(self.app, self.namespace)

        self.short_header = (
            'ID',
            'Name',
            'Router',
            'Subnet',
            'Flavor',
            'State',
            'Status',
        )

        self.short_data = (
            _vpnservice['id'],
            _vpnservice['name'],
            _vpnservice['router_id'],
            _vpnservice['subnet_id'],
            _vpnservice['flavor_id'],
            _vpnservice['admin_state_up'],
            _vpnservice['status'],
        )

        self.networkclient.vpn_services = mock.Mock(return_value=[_vpnservice])
        self.mocked = self.networkclient.vpn_services

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
        self.assertEqual([self.short_data], list(data))


class TestSetVPNService(TestVPNService, common.TestSetVPNaaS):

    def setUp(self):
        super(TestSetVPNService, self).setUp()
        self.networkclient.update_vpn_service = mock.Mock(
            return_value=_vpnservice)
        self.mocked = self.networkclient.update_vpn_service
        self.cmd = vpnservice.SetVPNSercice(self.app, self.namespace)

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


class TestShowVPNService(TestVPNService, common.TestShowVPNaaS):

    def setUp(self):
        super(TestShowVPNService, self).setUp()
        self.networkclient.get_vpn_service = mock.Mock(
            return_value=_vpnservice)
        self.mocked = self.networkclient.get_vpn_service
        self.cmd = vpnservice.ShowVPNService(self.app, self.namespace)
