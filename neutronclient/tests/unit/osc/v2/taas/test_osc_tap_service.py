# All Rights Reserved 2020
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

import copy
import operator
from unittest import mock

from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from openstack.network.v2 import tap_service
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util
from oslo_utils import uuidutils

from neutronclient.osc.v2.taas import tap_service as osc_tap_service
from neutronclient.tests.unit.osc.v2.taas import fakes


columns_long = tuple(col for col, _, listing_mode in osc_tap_service._attr_map
                     if listing_mode in (column_util.LIST_BOTH,
                                         column_util.LIST_LONG_ONLY))
headers_long = tuple(head for _, head, listing_mode in
                     osc_tap_service._attr_map if listing_mode in
                     (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY))
sorted_attr_map = sorted(osc_tap_service._attr_map, key=operator.itemgetter(1))
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(attrs, columns)


class TestCreateTapService(test_fakes.TestNeutronClientOSCV2):

    columns = (
        'id',
        'name',
        'port_id',
        'status',
    )

    def setUp(self):
        super().setUp()
        self.cmd = osc_tap_service.CreateTapService(self.app, self.namespace)

    def test_create_tap_service(self):
        """Test Create Tap Service."""
        port_id = uuidutils.generate_uuid()
        fake_tap_service = fakes.FakeTapService.create_tap_service(
            attrs={'port_id': port_id}
        )
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.create_tap_service = mock.Mock(
            return_value=fake_tap_service)
        self.app.client_manager.network.find_port = mock.Mock(
            return_value={'id': port_id})
        self.app.client_manager.network.find_tap_service = mock.Mock(
            side_effect=lambda _, name_or_id: {'id': name_or_id})
        arg_list = [
            '--name', fake_tap_service['name'],
            '--port', fake_tap_service['port_id'],
        ]

        verify_list = [
            ('name', fake_tap_service['name']),
            ('port_id', fake_tap_service['port_id']),
        ]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        self.app.client_manager.network.find_tap_service = mock.Mock(
            return_value=fake_tap_service)

        columns, data = self.cmd.take_action(parsed_args)
        create_tap_s_mock = self.app.client_manager.network.create_tap_service
        create_tap_s_mock.assert_called_once_with(
            **{'name': fake_tap_service['name'],
               'port_id': fake_tap_service['port_id']})
        self.assertEqual(self.columns, columns)
        fake_data = _get_data(
            fake_tap_service,
            osc_tap_service._get_columns(fake_tap_service)[1])
        self.assertEqual(fake_data, data)


class TestListTapService(test_fakes.TestNeutronClientOSCV2):
    def setUp(self):
        super().setUp()
        self.cmd = osc_tap_service.ListTapService(self.app, self.namespace)

    def test_list_tap_service(self):
        """Test List Tap Service."""
        fake_tap_services = fakes.FakeTapService.create_tap_services(
            attrs={'port_id': uuidutils.generate_uuid()},
            count=4)
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.tap_services = mock.Mock(
            return_value=fake_tap_services)

        arg_list = []
        verify_list = []

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)

        headers, data = self.cmd.take_action(parsed_args)

        self.app.client_manager.network.tap_services.assert_called_once()
        self.assertEqual(headers, list(headers_long))
        self.assertListItemEqual(
            list(data),
            [_get_data(fake_tap_service, columns_long) for fake_tap_service
             in fake_tap_services]
        )


class TestDeleteTapService(test_fakes.TestNeutronClientOSCV2):
    def setUp(self):
        super().setUp()
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.find_tap_service = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing:
            tap_service.TapService(id=name_or_id))
        self.cmd = osc_tap_service.DeleteTapService(self.app, self.namespace)

    def test_delete_tap_service(self):
        """Test Delete tap service."""

        fake_tap_service = fakes.FakeTapService.create_tap_service(
            attrs={'port_id': uuidutils.generate_uuid()}
        )
        self.app.client_manager.network.delete_tap_service = mock.Mock()

        arg_list = [
            fake_tap_service['id'],
        ]
        verify_list = [
            (osc_tap_service.TAP_SERVICE, [fake_tap_service['id']]),
        ]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        result = self.cmd.take_action(parsed_args)

        mock_delete_tap_s = self.app.client_manager.network.delete_tap_service
        mock_delete_tap_s.assert_called_once_with(fake_tap_service['id'])
        self.assertIsNone(result)


class TestShowTapService(test_fakes.TestNeutronClientOSCV2):
    columns = (
        'id',
        'name',
        'port_id',
        'status',
    )

    def setUp(self):
        super().setUp()
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.find_tap_service = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing:
            tap_service.TapService(id=name_or_id))
        self.cmd = osc_tap_service.ShowTapService(self.app, self.namespace)

    def test_show_tap_service(self):
        """Test Show tap service."""

        fake_tap_service = fakes.FakeTapService.create_tap_service(
            attrs={'port_id': uuidutils.generate_uuid()}
        )
        self.app.client_manager.network.get_tap_service = mock.Mock(
            return_value=fake_tap_service)
        arg_list = [
            fake_tap_service['id'],
        ]
        verify_list = [
            (osc_tap_service.TAP_SERVICE, fake_tap_service['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)

        headers, data = self.cmd.take_action(parsed_args)

        mock_get_tap_s = self.app.client_manager.network.get_tap_service
        mock_get_tap_s.assert_called_once_with(
            fake_tap_service['id'])
        self.assertEqual(self.columns, headers)
        fake_data = _get_data(
            fake_tap_service,
            osc_tap_service._get_columns(fake_tap_service)[1])
        self.assertItemEqual(fake_data, data)


class TestUpdateTapService(test_fakes.TestNeutronClientOSCV2):

    _new_name = 'new_name'

    columns = (
        'id',
        'name',
        'port_id',
        'status',
    )

    def setUp(self):
        super().setUp()
        self.cmd = osc_tap_service.UpdateTapService(self.app, self.namespace)
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.find_tap_service = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing:
            tap_service.TapService(id=name_or_id))

    def test_update_tap_service(self):
        """Test update tap service"""
        fake_tap_service = fakes.FakeTapService.create_tap_service(
            attrs={'port_id': uuidutils.generate_uuid()}
        )
        new_tap_service = copy.deepcopy(fake_tap_service)
        new_tap_service['name'] = self._new_name

        self.app.client_manager.network.update_tap_service = mock.Mock(
            return_value=new_tap_service)

        arg_list = [
            fake_tap_service['id'],
            '--name', self._new_name,
        ]
        verify_list = [('name', self._new_name)]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        columns, data = self.cmd.take_action(parsed_args)
        attrs = {'name': self._new_name}

        mock_update_tap_s = self.app.client_manager.network.update_tap_service
        mock_update_tap_s.assert_called_once_with(
            fake_tap_service['id'], **attrs)
        self.assertEqual(self.columns, columns)
        fake_data = _get_data(
            new_tap_service,
            osc_tap_service._get_columns(new_tap_service)[1])
        self.assertItemEqual(fake_data, data)
