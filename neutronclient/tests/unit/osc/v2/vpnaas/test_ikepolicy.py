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

from osc_lib.tests import utils as tests_utils

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.vpnaas import ikepolicy
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.vpnaas import common
from neutronclient.tests.unit.osc.v2.vpnaas import fakes


_ikepolicy = fakes.IKEPolicy().create()
CONVERT_MAP = {
    'project': 'project_id',
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _ikepolicy
    if data:
        source.update(data)
    return source


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = _ikepolicy
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestIKEPolicy(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: list(exp_req)}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super(TestIKEPolicy, self).setUp()

        def _mock_ikepolicy(*args, **kwargs):
            self.networkclient.find_vpn_ike_policy.assert_called_once_with(
                self.resource['id'], ignore_missing=False)
            return {'id': args[0]}

        self.networkclient.find_vpn_ike_policy.side_effect = mock.Mock(
            side_effect=_mock_ikepolicy)
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _ikepolicy['project_id']
        self.res = 'ikepolicy'
        self.res_plural = 'ikepolicies'
        self.resource = _ikepolicy
        self.headers = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encryption Algorithm',
            'IKE Version',
            'Perfect Forward Secrecy (PFS)',
            'Description',
            'Phase1 Negotiation Mode',
            'Project',
            'Lifetime',
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Authentication Algorithm',
            'Description',
            'Encryption Algorithm',
            'ID',
            'IKE Version',
            'Lifetime',
            'Name',
            'Perfect Forward Secrecy (PFS)',
            'Phase1 Negotiation Mode',
            'Project',
        )
        self.ordered_data = (
            _ikepolicy['auth_algorithm'],
            _ikepolicy['description'],
            _ikepolicy['encryption_algorithm'],
            _ikepolicy['id'],
            _ikepolicy['ike_version'],
            _ikepolicy['lifetime'],
            _ikepolicy['name'],
            _ikepolicy['pfs'],
            _ikepolicy['phase1_negotiation_mode'],
            _ikepolicy['project_id'],
        )
        self.ordered_columns = (
            'auth_algorithm',
            'description',
            'encryption_algorithm',
            'id',
            'ike_version',
            'lifetime',
            'name',
            'pfs',
            'phase1_negotiation_mode',
            'project_id',
        )


class TestCreateIKEPolicy(TestIKEPolicy, common.TestCreateVPNaaS):

    def setUp(self):
        super(TestCreateIKEPolicy, self).setUp()
        self.networkclient.create_vpn_ike_policy = mock.Mock(
            return_value=_ikepolicy)
        self.mocked = self.networkclient.create_vpn_ike_policy
        self.cmd = ikepolicy.CreateIKEPolicy(self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.networkclient.create_vpn_ikepolicy.return_value = response
        osc_utils.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name') or 'my-name'
        description = args.get('description') or 'my-desc'
        auth_algorithm = args.get('auth_algorithm') or 'sha1'
        encryption_algorithm = args.get('encryption_algorithm') or 'aes-128'
        phase1_negotiation_mode = args.get('phase1_negotiation_mode') or 'main'
        ike_version = args.get('ike_version') or 'v1'
        pfs = args.get('pfs') or 'group5'
        tenant_id = args.get('tenant_id') or 'my-tenant'
        arglist = [
            '--description', description,
            '--auth-algorithm', auth_algorithm,
            '--encryption-algorithm', encryption_algorithm,
            '--phase1-negotiation-mode', phase1_negotiation_mode,
            '--ike-version', ike_version,
            '--pfs', pfs,
            '--project', tenant_id,
            name,
        ]
        verifylist = [
            ('description', description),
            ('auth_algorithm', auth_algorithm),
            ('encryption_algorithm', encryption_algorithm),
            ('phase1_negotiation_mode', phase1_negotiation_mode),
            ('ike_version', ike_version),
            ('pfs', pfs),
            ('project', tenant_id),
            ('name', name),
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
        self._test_create_with_all_params({'name': 'new_ikepolicy'})

    def test_create_with_all_params_aggressive_mode(self):
        self._test_create_with_all_params(
            {'phase1_negotiation_mode': 'aggressive'})


class TestDeleteIKEPolicy(TestIKEPolicy, common.TestDeleteVPNaaS):

    def setUp(self):
        super(TestDeleteIKEPolicy, self).setUp()
        self.networkclient.delete_vpn_ike_policy = mock.Mock()
        self.mocked = self.networkclient.delete_vpn_ike_policy
        self.cmd = ikepolicy.DeleteIKEPolicy(self.app, self.namespace)


class TestListIKEPolicy(TestIKEPolicy):

    def setUp(self):
        super(TestListIKEPolicy, self).setUp()
        self.cmd = ikepolicy.ListIKEPolicy(self.app, self.namespace)

        self.short_header = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encryption Algorithm',
            'IKE Version',
            'Perfect Forward Secrecy (PFS)',
        )

        self.short_data = (
            _ikepolicy['id'],
            _ikepolicy['name'],
            _ikepolicy['auth_algorithm'],
            _ikepolicy['encryption_algorithm'],
            _ikepolicy['ike_version'],
            _ikepolicy['pfs'],
        )

        self.networkclient.vpn_ike_policies = mock.Mock(
            return_value=[_ikepolicy])
        self.mocked = self.networkclient.vpn_ike_policies

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


class TestSetIKEPolicy(TestIKEPolicy, common.TestSetVPNaaS):

    def setUp(self):
        super(TestSetIKEPolicy, self).setUp()
        self.networkclient.update_vpn_ike_policy = mock.Mock(
            return_value=_ikepolicy)
        self.mocked = self.networkclient.update_vpn_ike_policy
        self.cmd = ikepolicy.SetIKEPolicy(self.app, self.namespace)

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
            target, **{'auth_algorithm': 'sha256'})
        self.assertIsNone(result)

    def test_set_phase1_negotiation_mode_with_aggressive(self):
        target = self.resource['id']
        phase1_negotiation_mode = 'aggressive'
        arglist = [target,
                   '--phase1-negotiation-mode', phase1_negotiation_mode]
        verifylist = [
            (self.res, target),
            ('phase1_negotiation_mode', phase1_negotiation_mode),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'phase1_negotiation_mode': 'aggressive'})
        self.assertIsNone(result)


class TestShowIKEPolicy(TestIKEPolicy, common.TestShowVPNaaS):

    def setUp(self):
        super(TestShowIKEPolicy, self).setUp()
        self.networkclient.get_vpn_ike_policy = mock.Mock(
            return_value=_ikepolicy)
        self.mocked = self.networkclient.get_vpn_ike_policy
        self.cmd = ikepolicy.ShowIKEPolicy(self.app, self.namespace)
