#   Copyright 2017 FUJITSU LIMITED
#   All Rights Reserved
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

from osc_lib.tests import utils as tests_utils

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.vpnaas import endpoint_group
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.vpnaas import common
from neutronclient.tests.unit.osc.v2.vpnaas import fakes


_endpoint_group = fakes.EndpointGroup().create()
CONVERT_MAP = {
    'project': 'tenant_id',
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _endpoint_group
    if data:
        source.update(data)
    return source


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = _endpoint_group
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestEndpointGroup(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: list(exp_req)}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super(TestEndpointGroup, self).setUp()

        def _mock_endpoint_group(*args, **kwargs):
            self.networkclient.find_vpn_endpoint_group.assert_called_once_with(
                self.resource['id'], ignore_missing=False)
            return {'id': args[0]}

        self.networkclient.find_vpn_endpoint_group.side_effect = mock.Mock(
            side_effect=_mock_endpoint_group)
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _endpoint_group['project_id']
        self.res = 'endpoint_group'
        self.res_plural = 'endpoint_groups'
        self.resource = _endpoint_group
        self.headers = (
            'ID',
            'Name',
            'Type',
            'Endpoints',
            'Description',
            'Project',
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Description',
            'Endpoints',
            'ID',
            'Name',
            'Project',
            'Type',
        )
        self.ordered_data = (
            _endpoint_group['description'],
            _endpoint_group['endpoints'],
            _endpoint_group['id'],
            _endpoint_group['name'],
            _endpoint_group['project_id'],
            _endpoint_group['type'],
        )
        self.ordered_columns = (
            'description',
            'endpoints',
            'id',
            'name',
            'project_id',
            'type',
        )


class TestCreateEndpointGroup(TestEndpointGroup, common.TestCreateVPNaaS):

    def setUp(self):
        super(TestCreateEndpointGroup, self).setUp()
        self.networkclient.create_vpn_endpoint_group = mock.Mock(
            return_value=_endpoint_group)
        self.mocked = self.networkclient.create_vpn_endpoint_group
        self.cmd = endpoint_group.CreateEndpointGroup(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.neutronclient.create_endpoint_group.return_value = \
            {self.res: dict(response)}
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params_cidr(self, args={}):
        name = args.get('name') or 'my-name'
        description = args.get('description') or 'my-desc'
        endpoint_type = args.get('type') or 'cidr'
        endpoints = args.get('endpoints') or ['10.0.0.0/24', '20.0.0.0/24']
        tenant_id = args.get('project_id') or 'my-tenant'
        arglist = [
            '--description', description,
            '--type', endpoint_type,
            '--value', '10.0.0.0/24',
            '--value', '20.0.0.0/24',
            '--project', tenant_id,
            name,
        ]
        verifylist = [
            ('description', description),
            ('type', endpoint_type),
            ('endpoints', endpoints),
            ('project', tenant_id),
            ('name', name),
        ]
        return arglist, verifylist

    def _test_create_with_all_params_cidr(self, args={}):
        arglist, verifylist = self._set_all_params_cidr(args)
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_with_all_params_cidr(self):
        self._test_create_with_all_params_cidr()


class TestDeleteEndpointGroup(TestEndpointGroup, common.TestDeleteVPNaaS):

    def setUp(self):
        super(TestDeleteEndpointGroup, self).setUp()
        self.networkclient.delete_vpn_endpoint_group = mock.Mock()
        self.mocked = self.networkclient.delete_vpn_endpoint_group
        self.cmd = endpoint_group.DeleteEndpointGroup(self.app, self.namespace)


class TestListEndpointGroup(TestEndpointGroup):

    def setUp(self):
        super(TestListEndpointGroup, self).setUp()
        self.cmd = endpoint_group.ListEndpointGroup(self.app, self.namespace)

        self.short_header = (
            'ID',
            'Name',
            'Type',
            'Endpoints',
        )

        self.short_data = (
            _endpoint_group['id'],
            _endpoint_group['name'],
            _endpoint_group['type'],
            _endpoint_group['endpoints'],
        )

        self.networkclient.vpn_endpoint_groups = mock.Mock(
            return_value=[_endpoint_group])
        self.mocked = self.networkclient.vpn_endpoint_groups

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


class TestSetEndpointGroup(TestEndpointGroup, common.TestSetVPNaaS):

    def setUp(self):
        super(TestSetEndpointGroup, self).setUp()
        self.networkclient.update_vpn_endpoint_group = mock.Mock(
            return_value=_endpoint_group)
        self.mocked = self.networkclient.update_vpn_endpoint_group
        self.cmd = endpoint_group.SetEndpointGroup(self.app, self.namespace)


class TestShowEndpointGroup(TestEndpointGroup, common.TestShowVPNaaS):

    def setUp(self):
        super(TestShowEndpointGroup, self).setUp()
        self.networkclient.get_vpn_endpoint_group = mock.Mock(
            return_value=_endpoint_group)
        self.mocked = self.networkclient.get_vpn_endpoint_group
        self.cmd = endpoint_group.ShowEndpointGroup(self.app, self.namespace)
