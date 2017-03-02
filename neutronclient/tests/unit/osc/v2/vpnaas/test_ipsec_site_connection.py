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
from osc_lib.cli import format_columns
from osc_lib.tests import utils as tests_utils

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.vpnaas import ipsec_site_connection
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.vpnaas import common
from neutronclient.tests.unit.osc.v2.vpnaas import fakes


_ipsec_site_conn = fakes.IPsecSiteConnection().create_conn()
CONVERT_MAP = {
    'project': 'tenant_id',
    'ikepolicy': 'ikepolicy_id',
    'ipsecpolicy': 'ipsecpolicy_id',
    'vpnservice': 'vpnservice_id',
    'peer_endpoint_group': 'peer_ep_group_id',
    'local_endpoint_group': 'local_ep_group_id',
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _ipsec_site_conn
    if data:
        source.update(data)
    return (
        _ipsec_site_conn['id'],
        _ipsec_site_conn['name'],
        _ipsec_site_conn['peer_address'],
        _ipsec_site_conn['auth_mode'],
        _ipsec_site_conn['status'],
        _ipsec_site_conn['tenant_id'],
        format_columns.ListColumn(_ipsec_site_conn['peer_cidrs']),
        _ipsec_site_conn['vpnservice_id'],
        _ipsec_site_conn['ipsecpolicy_id'],
        _ipsec_site_conn['ikepolicy_id'],
        _ipsec_site_conn['mtu'],
        _ipsec_site_conn['initiator'],
        _ipsec_site_conn['admin_state_up'],
        _ipsec_site_conn['description'],
        _ipsec_site_conn['psk'],
        _ipsec_site_conn['route_mode'],
        _ipsec_site_conn['local_id'],
        _ipsec_site_conn['peer_id'],
        _ipsec_site_conn['local_ep_group_id'],
        _ipsec_site_conn['peer_ep_group_id'],
    )


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = copy.deepcopy(_ipsec_site_conn)
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestIPsecSiteConn(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = {self.res: exp_req}
        self.mocked.assert_called_once_with(req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertItemEqual(self.ordered_data, data)

    def setUp(self):
        super(TestIPsecSiteConn, self).setUp()

        def _mock_ipsec_site_conn(*args, **kwargs):
            return {'id': args[1]}

        self.neutronclient.find_resource.side_effect = mock.Mock(
            side_effect=_mock_ipsec_site_conn)
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _ipsec_site_conn['tenant_id']
        self.res = 'ipsec_site_connection'
        self.res_plural = 'ipsec_site_connections'
        self.resource = _ipsec_site_conn
        self.headers = (
            'ID',
            'Name',
            'Peer Address',
            'Authentication Algorithm',
            'Status',
            'Project',
            'Peer CIDRs',
            'VPN Service',
            'IPSec Policy',
            'IKE Policy',
            'MTU',
            'Initiator',
            'State',
            'Description',
            'Pre-shared Key',
            'Route Mode',
            'Local ID',
            'Peer ID',
            'Local Endpoint Group ID',
            'Peer Endpoint Group ID'
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Authentication Algorithm',
            'Description',
            'ID',
            'IKE Policy',
            'IPSec Policy',
            'Initiator',
            'Local Endpoint Group ID',
            'Local ID',
            'MTU',
            'Name',
            'Peer Address',
            'Peer CIDRs',
            'Peer Endpoint Group ID',
            'Peer ID',
            'Pre-shared Key',
            'Project',
            'Route Mode',
            'State',
            'Status',
            'VPN Service',
        )
        self.ordered_data = (
            _ipsec_site_conn['auth_mode'],
            _ipsec_site_conn['description'],
            _ipsec_site_conn['id'],
            _ipsec_site_conn['ikepolicy_id'],
            _ipsec_site_conn['ipsecpolicy_id'],
            _ipsec_site_conn['initiator'],
            _ipsec_site_conn['local_ep_group_id'],
            _ipsec_site_conn['local_id'],
            _ipsec_site_conn['mtu'],
            _ipsec_site_conn['name'],
            _ipsec_site_conn['peer_address'],
            format_columns.ListColumn(_ipsec_site_conn['peer_cidrs']),
            _ipsec_site_conn['peer_ep_group_id'],
            _ipsec_site_conn['peer_id'],
            _ipsec_site_conn['psk'],
            _ipsec_site_conn['tenant_id'],
            _ipsec_site_conn['route_mode'],
            _ipsec_site_conn['admin_state_up'],
            _ipsec_site_conn['status'],
            _ipsec_site_conn['vpnservice_id'],
        )


class TestCreateIPsecSiteConn(TestIPsecSiteConn, common.TestCreateVPNaaS):

    def setUp(self):
        super(TestCreateIPsecSiteConn, self).setUp()
        self.neutronclient.create_ipsec_site_connection = mock.Mock(
            return_value={self.res: _ipsec_site_conn})
        self.mocked = self.neutronclient.create_ipsec_site_connection
        self.cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            self.app, self.namespace)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.neutronclient.create_ipsec_site_connection.return_value = \
            {self.res: dict(response)}
        osc_utils.find_project.return_value.id = response['tenant_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = (
            response['auth_mode'],
            response['description'],
            response['id'],
            response['ikepolicy_id'],
            response['ipsecpolicy_id'],
            response['initiator'],
            response['local_ep_group_id'],
            response['local_id'],
            response['mtu'],
            response['name'],
            response['peer_address'],
            format_columns.ListColumn(response['peer_cidrs']),
            response['peer_ep_group_id'],
            response['peer_id'],
            response['psk'],
            response['tenant_id'],
            response['route_mode'],
            response['admin_state_up'],
            response['status'],
            response['vpnservice_id'],
        )

    def _set_all_params(self, args={}):
        tenant_id = args.get('tenant_id') or 'my-tenant'
        name = args.get('name') or 'connection1'
        peer_address = args.get('peer_address') or '192.168.2.10'
        peer_id = args.get('peer_id') or '192.168.2.10'
        psk = args.get('psk') or 'abcd'
        mtu = args.get('mtu') or '1500'
        initiator = args.get('initiator') or 'bi-directional'
        vpnservice_id = args.get('vpnservice') or 'vpnservice_id'
        ikepolicy_id = args.get('ikepolicy') or 'ikepolicy_id'
        ipsecpolicy_id = args.get('ipsecpolicy') or 'ipsecpolicy_id'
        local_ep_group = args.get('local_ep_group_id') or 'local-epg'
        peer_ep_group = args.get('peer_ep_group_id') or 'peer-epg'
        description = args.get('description') or 'my-vpn-connection'

        arglist = [
            '--project', tenant_id,
            '--peer-address', peer_address,
            '--peer-id', peer_id,
            '--psk', psk,
            '--initiator', initiator,
            '--vpnservice', vpnservice_id,
            '--ikepolicy', ikepolicy_id,
            '--ipsecpolicy', ipsecpolicy_id,
            '--mtu', mtu,
            '--description', description,
            '--local-endpoint-group', local_ep_group,
            '--peer-endpoint-group', peer_ep_group,
            name,
        ]
        verifylist = [
            ('project', tenant_id),
            ('peer_address', peer_address),
            ('peer_id', peer_id),
            ('psk', psk),
            ('initiator', initiator),
            ('vpnservice', vpnservice_id),
            ('ikepolicy', ikepolicy_id),
            ('ipsecpolicy', ipsecpolicy_id),
            ('mtu', mtu),
            ('description', description),
            ('local_endpoint_group', local_ep_group),
            ('peer_endpoint_group', peer_ep_group),
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


class TestDeleteIPsecSiteConn(TestIPsecSiteConn, common.TestDeleteVPNaaS):

    def setUp(self):
        super(TestDeleteIPsecSiteConn, self).setUp()
        self.neutronclient.delete_ipsec_site_connection = mock.Mock(
            return_value={self.res: _ipsec_site_conn})
        self.mocked = self.neutronclient.delete_ipsec_site_connection
        self.cmd = ipsec_site_connection.DeleteIPsecSiteConnection(
            self.app, self.namespace)


class TestListIPsecSiteConn(TestIPsecSiteConn):

    def setUp(self):
        super(TestListIPsecSiteConn, self).setUp()
        self.cmd = ipsec_site_connection.ListIPsecSiteConnection(
            self.app, self.namespace)

        self.short_header = (
            'ID',
            'Name',
            'Peer Address',
            'Authentication Algorithm',
            'Status',
        )

        self.short_data = (
            _ipsec_site_conn['id'],
            _ipsec_site_conn['name'],
            _ipsec_site_conn['peer_address'],
            _ipsec_site_conn['auth_mode'],
            _ipsec_site_conn['status'],
        )

        self.neutronclient.list_ipsec_site_connections = mock.Mock(
            return_value={self.res_plural: [_ipsec_site_conn]})
        self.mocked = self.neutronclient.list_ipsec_site_connections

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)
        self.assertListItemEqual([self.data], list(data))

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetIPsecSiteConn(TestIPsecSiteConn, common.TestSetVPNaaS):

    def setUp(self):
        super(TestSetIPsecSiteConn, self).setUp()
        self.neutronclient.update_ipsec_site_connection = mock.Mock(
            return_value={self.res: _ipsec_site_conn})
        self.mocked = self.neutronclient.update_ipsec_site_connection
        self.cmd = ipsec_site_connection.SetIPsecSiteConnection(
            self.app, self.namespace)

    def test_set_ipsec_site_conn_with_peer_id(self):
        target = self.resource['id']
        peer_id = '192.168.3.10'
        arglist = [target, '--peer-id', peer_id]
        verifylist = [
            (self.res, target),
            ('peer_id', peer_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {self.res: {'peer_id': peer_id}})
        self.assertIsNone(result)


class TestShowIPsecSiteConn(TestIPsecSiteConn, common.TestShowVPNaaS):

    def setUp(self):
        super(TestShowIPsecSiteConn, self).setUp()
        self.neutronclient.show_ipsec_site_connection = mock.Mock(
            return_value={self.res: _ipsec_site_conn})
        self.mocked = self.neutronclient.show_ipsec_site_connection
        self.cmd = ipsec_site_connection.ShowIPsecSiteConnection(
            self.app, self.namespace)
