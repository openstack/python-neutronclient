# Copyright (c) 2018 Orange SA.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import operator
from unittest import mock

from osc_lib.tests.utils import ParserException
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from neutronclient.tests.unit.osc.v2.networking_bgpvpn import fakes


columns_short = tuple(col for col, _, listing_mode
                      in fakes.BgpvpnFakeRouterAssoc._attr_map
                      if listing_mode in (column_util.LIST_BOTH,
                                          column_util.LIST_SHORT_ONLY))
columns_long = tuple(col for col, _, listing_mode
                     in fakes.BgpvpnFakeRouterAssoc._attr_map
                     if listing_mode in (column_util.LIST_BOTH,
                                         column_util.LIST_LONG_ONLY))
headers_short = tuple(head for _, head, listing_mode
                      in fakes.BgpvpnFakeRouterAssoc._attr_map
                      if listing_mode in (column_util.LIST_BOTH,
                                          column_util.LIST_SHORT_ONLY))
headers_long = tuple(head for _, head, listing_mode
                     in fakes.BgpvpnFakeRouterAssoc._attr_map
                     if listing_mode in (column_util.LIST_BOTH,
                                         column_util.LIST_LONG_ONLY))
sorted_attr_map = sorted(fakes.BgpvpnFakeRouterAssoc._attr_map,
                         key=operator.itemgetter(1))
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(
        attrs, columns, formatters=fakes.BgpvpnFakeAssoc._formatters)


class TestCreateRouterAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super(TestCreateRouterAssoc, self).setUp()
        self.cmd = fakes.CreateBgpvpnFakeRouterAssoc(self.app, self.namespace)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.fake_router = fakes.create_one_resource()
        self.networkclient.find_bgpvpn = mock.Mock(
            side_effect=lambda name_or_id: {'id': name_or_id})
        self.networkclient.find_fake_resource = mock.Mock(
            side_effect=lambda name_or_id: {'id': name_or_id})

    def _build_args(self, param=None):
        arglist_base = [
            self.fake_bgpvpn['id'],
            self.fake_router['id'],
            '--project', self.fake_bgpvpn['tenant_id']
        ]
        if param is not None:
            if isinstance(param, list):
                arglist_base.extend(param)
            else:
                arglist_base.append(param)
        return arglist_base

    def _build_verify_list(self, param=None):
        verifylist = [
            ('bgpvpn', self.fake_bgpvpn['id']),
            ('resource', self.fake_router['id']),
            ('project', self.fake_bgpvpn['tenant_id'])
        ]
        if param is not None:
            verifylist.append(param)
        return verifylist

    def _exec_create_router_association(
            self, fake_res_assoc, arglist, verifylist):

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, data = self.cmd.take_action(parsed_args)

        fake_res_assoc_call = {
            'fake_resource_id': 'fake_resource_id',
            'tenant_id': 'fake_project_id'
        }
        for key, value in verifylist:
            if value not in fake_res_assoc_call.values():
                fake_res_assoc_call[key] = value
        fake_res_assoc_call.pop('bgpvpn')

        self.networkclient.create_bgpvpn_router_association.\
            assert_called_once_with(
                self.fake_bgpvpn['id'],
                **fake_res_assoc_call)
        return cols, data

    def test_create_router_association(self):
        fake_res_assoc = fakes.create_one_resource_association(
            self.fake_router)

        self.networkclient.create_bgpvpn_router_association = mock.Mock(
            return_value={
                fakes.BgpvpnFakeRouterAssoc._resource: fake_res_assoc,
                'advertise_extra_routes': True})

        arglist = self._build_args()
        # advertise_extra_routes will be False since none
        # of the mutually exclusive args present
        verifylist = self._build_verify_list(('advertise_extra_routes', False))

        self._exec_create_router_association(
            fake_res_assoc, arglist, verifylist)

    def test_create_router_association_advertise(self):
        fake_res_assoc = fakes.create_one_resource_association(
            self.fake_router,
            {'advertise_extra_routes': True})

        self.networkclient.create_bgpvpn_router_association = mock.Mock(
            return_value=fake_res_assoc)

        arglist = self._build_args('--advertise_extra_routes')
        verifylist = self._build_verify_list(('advertise_extra_routes', True))

        cols, data = self._exec_create_router_association(
            fake_res_assoc, arglist, verifylist)
        self.assertEqual(sorted_columns, cols)
        self.assertEqual(_get_data(fake_res_assoc), data)

    def test_create_router_association_no_advertise(self):
        fake_res_assoc = fakes.create_one_resource_association(
            self.fake_router,
            {'advertise_extra_routes': False})

        self.networkclient.create_bgpvpn_router_association = mock.Mock(
            return_value=fake_res_assoc)

        arglist = self._build_args('--no-advertise_extra_routes')
        verifylist = self._build_verify_list(('advertise_extra_routes', False))

        cols, data = self._exec_create_router_association(
            fake_res_assoc, arglist, verifylist)
        self.assertEqual(sorted_columns, cols)
        self.assertEqual(_get_data(fake_res_assoc), data)

    def test_create_router_association_advertise_fault(self):
        arglist = self._build_args(
            ['--advertise_extra_routes', '--no-advertise_extra_routes'])

        try:
            self._exec_create_router_association(None, arglist, None)
        except ParserException as e:
            self.assertEqual(format(e), 'Argument parse failed')

    def test_router_association_unknown_arg(self):
        arglist = self._build_args('--unknown arg')

        try:
            self._exec_create_router_association(None, arglist, None)
        except ParserException as e:
            self.assertEqual(format(e), 'Argument parse failed')


class TestSetRouterAssoc(fakes.TestNeutronClientBgpvpn):

    def setUp(self):
        super(TestSetRouterAssoc, self).setUp()
        self.cmd = fakes.SetBgpvpnFakeRouterAssoc(self.app, self.namespace)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.fake_router = fakes.create_one_resource()
        self.networkclient.find_bgpvpn = mock.Mock(
            side_effect=lambda name_or_id: {'id': name_or_id})

    def _build_args(self, fake_res_assoc, param=None):
        arglist_base = [
            fake_res_assoc['id'],
            self.fake_bgpvpn['id']
        ]
        if param is not None:
            if isinstance(param, list):
                arglist_base.extend(param)
            else:
                arglist_base.append(param)
        return arglist_base

    def _build_verify_list(self, fake_res_assoc, param=None):
        verifylist = [
            ('resource_association_id', fake_res_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id'])
        ]
        if param is not None:
            verifylist.append(param)
        return verifylist

    def test_set_router_association_no_advertise(self):
        fake_res_assoc = fakes.create_one_resource_association(
            self.fake_router,
            {'advertise_extra_routes': True})
        self.networkclient.update_bgpvpn_router_association = \
            mock.Mock()

        arglist = self._build_args(
            fake_res_assoc,
            '--no-advertise_extra_routes')
        verifylist = [
            ('resource_association_id', fake_res_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.networkclient.update_bgpvpn_router_association.\
            assert_called_once_with(
                self.fake_bgpvpn['id'],
                fake_res_assoc['id'],
                **{'advertise_extra_routes': False}
            )
        self.assertIsNone(result)

    def test_set_router_association_advertise(self):
        fake_res_assoc = fakes.create_one_resource_association(
            self.fake_router,
            {'advertise_extra_routes': False})
        self.networkclient.update_bgpvpn_router_association = \
            mock.Mock()

        arglist = self._build_args(
            fake_res_assoc,
            '--advertise_extra_routes')
        verifylist = [
            ('resource_association_id', fake_res_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.networkclient.update_bgpvpn_router_association.\
            assert_called_once_with(
                self.fake_bgpvpn['id'],
                fake_res_assoc['id'],
                **{'advertise_extra_routes': True}
            )
        self.assertIsNone(result)


class TestShowRouterAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super(TestShowRouterAssoc, self).setUp()
        self.cmd = fakes.ShowBgpvpnFakeRouterAssoc(self.app, self.namespace)
        self.networkclient.find_bgpvpn = mock.Mock(
            side_effect=lambda name_or_id: {'id': name_or_id})

    def test_show_router_association(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_res = fakes.create_one_resource()
        fake_res_assoc = fakes.create_one_resource_association(
            fake_res,
            {'advertise_extra_routes': True})
        self.networkclient.get_bgpvpn_router_association = mock.Mock(
            return_value=fake_res_assoc)
        arglist = [
            fake_res_assoc['id'],
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('resource_association_id', fake_res_assoc['id']),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, data = self.cmd.take_action(parsed_args)

        self.networkclient.get_bgpvpn_router_association.\
            assert_called_once_with(fake_bgpvpn['id'], fake_res_assoc['id'])
        self.assertEqual(sorted_columns, cols)
        self.assertEqual(data, _get_data(fake_res_assoc))
