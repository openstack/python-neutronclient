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

import copy

import mock
from osc_lib.tests import utils as tests_utils

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.vpnaas import ipsecpolicy
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.vpnaas import common
from neutronclient.tests.unit.osc.v2.vpnaas import fakes


_ipsecpolicy = fakes.IPSecPolicy().create()
CONVERT_MAP = {
    'project': 'tenant_id',
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _ipsecpolicy
    if data:
        source.update(data)
    return tuple(source[key] for key in source)


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = copy.deepcopy(_ipsecpolicy)
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestIPSecPolicy(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = {self.res: exp_req}
        self.mocked.assert_called_once_with(req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super(TestIPSecPolicy, self).setUp()

        def _mock_ipsecpolicy(*args, **kwargs):
            self.neutronclient.find_resource.assert_called_once_with(
                self.res, self.resource['id'], cmd_resource='ipsecpolicy')
            return {'id': args[1]}

        self.neutronclient.find_resource.side_effect = mock.Mock(
            side_effect=_mock_ipsecpolicy)
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _ipsecpolicy['tenant_id']
        self.res = 'ipsecpolicy'
        self.res_plural = 'ipsecpolicies'
        self.resource = _ipsecpolicy
        self.headers = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encapsulation Mode',
            'Transform Protocol',
            'Encryption Algorithm',
            'Perfect Forward Secrecy (PFS)',
            'Description',
            'Project',
            'Lifetime',
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Authentication Algorithm',
            'Description',
            'Encapsulation Mode',
            'Encryption Algorithm',
            'ID',
            'Lifetime',
            'Name',
            'Perfect Forward Secrecy (PFS)',
            'Project',
            'Transform Protocol',
        )
        self.ordered_data = (
            _ipsecpolicy['auth_algorithm'],
            _ipsecpolicy['description'],
            _ipsecpolicy['encapsulation_mode'],
            _ipsecpolicy['encryption_algorithm'],
            _ipsecpolicy['id'],
            _ipsecpolicy['lifetime'],
            _ipsecpolicy['name'],
            _ipsecpolicy['pfs'],
            _ipsecpolicy['tenant_id'],
            _ipsecpolicy['transform_protocol'],
        )
        self.ordered_columns = (
            'auth_algorithm',
            'description',
            'encapsulation_mode',
            'encryption_algorithm',
            'id',
            'lifetime',
            'name',
            'pfs',
            'tenant_id',
            'transform_protocol',
        )


class TestCreateIPSecPolicy(TestIPSecPolicy, common.TestCreateVPNaaS):

    def setUp(self):
        super(TestCreateIPSecPolicy, self).setUp()
        self.neutronclient.create_ipsecpolicy = mock.Mock(
            return_value={self.res: _ipsecpolicy})
        self.mocked = self.neutronclient.create_ipsecpolicy
        self.cmd = ipsecpolicy.CreateIPsecPolicy(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.neutronclient.create_ipsecpolicy.return_value = \
            {self.res: dict(response)}
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name') or 'my-name'
        auth_algorithm = args.get('auth_algorithm') or 'sha1'
        encapsulation_mode = args.get('encapsulation_mode') or 'tunnel'
        transform_protocol = args.get('transform_protocol') or 'esp'
        encryption_algorithm = args.get('encryption_algorithm') or 'aes-128'
        pfs = args.get('pfs') or 'group5'
        description = args.get('description') or 'my-desc'
        tenant_id = args.get('tenant_id') or 'my-tenant'
        arglist = [
            name,
            '--auth-algorithm', auth_algorithm,
            '--encapsulation-mode', encapsulation_mode,
            '--transform-protocol', transform_protocol,
            '--encryption-algorithm', encryption_algorithm,
            '--pfs', pfs,
            '--description', description,
            '--project', tenant_id,
        ]
        verifylist = [
            ('name', name),
            ('auth_algorithm', auth_algorithm),
            ('encapsulation_mode', encapsulation_mode),
            ('transform_protocol', transform_protocol),
            ('encryption_algorithm', encryption_algorithm),
            ('pfs', pfs),
            ('description', description),
            ('project', tenant_id),
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

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_with_all_params(self):
        self._test_create_with_all_params()

    def test_create_with_all_params_name(self):
        self._test_create_with_all_params({'name': 'new_ipsecpolicy'})


class TestDeleteIPSecPolicy(TestIPSecPolicy, common.TestDeleteVPNaaS):

    def setUp(self):
        super(TestDeleteIPSecPolicy, self).setUp()
        self.neutronclient.delete_ipsecpolicy = mock.Mock(
            return_value={self.res: _ipsecpolicy})
        self.mocked = self.neutronclient.delete_ipsecpolicy
        self.cmd = ipsecpolicy.DeleteIPsecPolicy(self.app, self.namespace)


class TestListIPSecPolicy(TestIPSecPolicy):

    def setUp(self):
        super(TestListIPSecPolicy, self).setUp()
        self.cmd = ipsecpolicy.ListIPsecPolicy(self.app, self.namespace)

        self.short_header = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encapsulation Mode',
            'Transform Protocol',
            'Encryption Algorithm',
        )

        self.short_data = (
            _ipsecpolicy['id'],
            _ipsecpolicy['name'],
            _ipsecpolicy['auth_algorithm'],
            _ipsecpolicy['encapsulation_mode'],
            _ipsecpolicy['transform_protocol'],
            _ipsecpolicy['encryption_algorithm'],
        )

        self.neutronclient.list_ipsecpolicies = mock.Mock(
            return_value={self.res_plural: [_ipsecpolicy]})
        self.mocked = self.neutronclient.list_ipsecpolicies

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)
        self.assertEqual([self.data], list(data))

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetIPSecPolicy(TestIPSecPolicy, common.TestSetVPNaaS):

    def setUp(self):
        super(TestSetIPSecPolicy, self).setUp()
        self.neutronclient.update_ipsecpolicy = mock.Mock(
            return_value={self.res: _ipsecpolicy})
        self.mocked = self.neutronclient.update_ipsecpolicy
        self.cmd = ipsecpolicy.SetIPsecPolicy(self.app, self.namespace)

    def test_set_auth_algorithm_with_sha256(self):
        target = self.resource['id']
        auth_algorithm = 'sha256'
        arglist = [target, '--auth-algorithm', auth_algorithm]
        verifylist = [
            (self.res, target),
            ('auth_algorithm', auth_algorithm),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'auth_algorithm': 'sha256'}})
        self.assertIsNone(result)


class TestShowIPSecPolicy(TestIPSecPolicy, common.TestShowVPNaaS):

    def setUp(self):
        super(TestShowIPSecPolicy, self).setUp()
        self.neutronclient.show_ipsecpolicy = mock.Mock(
            return_value={self.res: _ipsecpolicy})
        self.mocked = self.neutronclient.show_ipsecpolicy
        self.cmd = ipsecpolicy.ShowIPsecPolicy(self.app, self.namespace)
