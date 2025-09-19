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
from openstack.network.v2 import tap_mirror
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util
from oslo_utils import uuidutils

from neutronclient.osc.v2.taas import tap_mirror as osc_tap_mirror
from neutronclient.tests.unit.osc.v2.taas import fakes


columns_long = tuple(col for col, _, listing_mode in osc_tap_mirror._attr_map
                     if listing_mode in (column_util.LIST_BOTH,
                                         column_util.LIST_LONG_ONLY))
headers_long = tuple(head for _, head, listing_mode in
                     osc_tap_mirror._attr_map if listing_mode in
                     (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY))
sorted_attr_map = sorted(osc_tap_mirror._attr_map, key=operator.itemgetter(1))
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(attrs, columns)


class TestCreateTapMirror(test_fakes.TestNeutronClientOSCV2):

    columns = (
        'directions',
        'id',
        'mirror_type',
        'name',
        'port_id',
        'remote_ip',
    )

    def setUp(self):
        super().setUp()
        self.cmd = osc_tap_mirror.CreateTapMirror(self.app, self.namespace)

    def test_create_tap_mirror(self):
        port_id = uuidutils.generate_uuid()
        fake_tap_mirror = fakes.FakeTapMirror.create_tap_mirror(
            attrs={'port_id': port_id}
        )
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.create_tap_mirror = mock.Mock(
            return_value=fake_tap_mirror)
        self.app.client_manager.network.find_port = mock.Mock(
            return_value={'id': port_id})
        self.app.client_manager.network.find_tap_mirror = mock.Mock(
            side_effect=lambda _, name_or_id: {'id': name_or_id})
        arg_list = [
            '--name', fake_tap_mirror['name'],
            '--port', fake_tap_mirror['port_id'],
            '--directions', fake_tap_mirror['directions'],
            '--remote-ip', fake_tap_mirror['remote_ip'],
            '--mirror-type', fake_tap_mirror['mirror_type'],
        ]

        verify_directions = fake_tap_mirror['directions'].split('=')
        verify_directions_dict = {verify_directions[0]: verify_directions[1]}

        verify_list = [
            ('name', fake_tap_mirror['name']),
            ('port_id', fake_tap_mirror['port_id']),
            ('directions', verify_directions_dict),
            ('remote_ip', fake_tap_mirror['remote_ip']),
            ('mirror_type', fake_tap_mirror['mirror_type']),
        ]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        self.app.client_manager.network.find_tap_mirror = mock.Mock(
            return_value=fake_tap_mirror)

        columns, data = self.cmd.take_action(parsed_args)
        create_tap_m_mock = self.app.client_manager.network.create_tap_mirror
        create_tap_m_mock.assert_called_once_with(
            **{'name': fake_tap_mirror['name'],
               'port_id': fake_tap_mirror['port_id'],
               'directions': verify_directions_dict,
               'remote_ip': fake_tap_mirror['remote_ip'],
               'mirror_type': fake_tap_mirror['mirror_type']})
        self.assertEqual(self.columns, columns)
        fake_data = _get_data(
            fake_tap_mirror,
            osc_tap_mirror._get_columns(fake_tap_mirror)[1])
        self.assertEqual(fake_data, data)


class TestListTapMirror(test_fakes.TestNeutronClientOSCV2):

    def setUp(self):
        super().setUp()
        self.cmd = osc_tap_mirror.ListTapMirror(self.app, self.namespace)

    def test_list_tap_mirror(self):
        """Test List Tap Mirror."""
        fake_tap_mirrors = fakes.FakeTapMirror.create_tap_mirrors(
            attrs={'port_id': uuidutils.generate_uuid()},
            count=4)
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.tap_mirrors = mock.Mock(
            return_value=fake_tap_mirrors)

        arg_list = []
        verify_list = []

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)

        headers, data = self.cmd.take_action(parsed_args)

        self.app.client_manager.network.tap_mirrors.assert_called_once()
        self.assertEqual(headers, list(headers_long))
        self.assertListItemEqual(
            list(data),
            [_get_data(fake_tap_mirror, columns_long) for fake_tap_mirror
             in fake_tap_mirrors]
        )


class TestDeleteTapMirror(test_fakes.TestNeutronClientOSCV2):

    def setUp(self):
        super().setUp()
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.find_tap_mirror = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing:
            tap_mirror.TapMirror(id=name_or_id))
        self.cmd = osc_tap_mirror.DeleteTapMirror(self.app, self.namespace)

    def test_delete_tap_mirror(self):
        """Test Delete Tap Mirror."""

        fake_tap_mirror = fakes.FakeTapMirror.create_tap_mirror(
            attrs={'port_id': uuidutils.generate_uuid()}
        )
        self.app.client_manager.network.delete_tap_mirror = mock.Mock()

        arg_list = [
            fake_tap_mirror['id'],
        ]
        verify_list = [
            (osc_tap_mirror.TAP_MIRROR, [fake_tap_mirror['id']]),
        ]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        result = self.cmd.take_action(parsed_args)

        mock_delete_tap_m = self.app.client_manager.network.delete_tap_mirror
        mock_delete_tap_m.assert_called_once_with(fake_tap_mirror['id'])
        self.assertIsNone(result)


class TestShowTapMirror(test_fakes.TestNeutronClientOSCV2):

    columns = (
        'directions',
        'id',
        'mirror_type',
        'name',
        'port_id',
        'remote_ip',
    )

    def setUp(self):
        super().setUp()
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.find_tap_mirror = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing:
            tap_mirror.TapMirror(id=name_or_id))
        self.cmd = osc_tap_mirror.ShowTapMirror(self.app, self.namespace)

    def test_show_tap_mirror(self):
        """Test Show Tap Mirror."""

        fake_tap_mirror = fakes.FakeTapMirror.create_tap_mirror(
            attrs={'port_id': uuidutils.generate_uuid()}
        )
        self.app.client_manager.network.get_tap_mirror = mock.Mock(
            return_value=fake_tap_mirror)
        arg_list = [
            fake_tap_mirror['id'],
        ]
        verify_list = [
            (osc_tap_mirror.TAP_MIRROR, fake_tap_mirror['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)

        headers, data = self.cmd.take_action(parsed_args)

        mock_get_tap_m = self.app.client_manager.network.get_tap_mirror
        mock_get_tap_m.assert_called_once_with(
            fake_tap_mirror['id'])
        self.assertEqual(self.columns, headers)
        fake_data = _get_data(
            fake_tap_mirror,
            osc_tap_mirror._get_columns(fake_tap_mirror)[1])
        self.assertItemEqual(fake_data, data)


class TestUpdateTapMirror(test_fakes.TestNeutronClientOSCV2):

    _new_name = 'new_name'
    columns = (
        'directions',
        'id',
        'mirror_type',
        'name',
        'port_id',
        'remote_ip',
    )

    def setUp(self):
        super().setUp()
        self.cmd = osc_tap_mirror.UpdateTapMirror(self.app, self.namespace)
        self.app.client_manager.network = mock.Mock()
        self.app.client_manager.network.find_tap_mirror = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing:
            tap_mirror.TapMirror(id=name_or_id))

    def test_update_tap_mirror(self):
        """Test update Tap Mirror"""
        fake_tap_mirror = fakes.FakeTapMirror.create_tap_mirror(
            attrs={'port_id': uuidutils.generate_uuid()}
        )
        new_tap_mirror = copy.deepcopy(fake_tap_mirror)
        new_tap_mirror['name'] = self._new_name

        self.app.client_manager.network.update_tap_mirror = mock.Mock(
            return_value=new_tap_mirror)

        arg_list = [
            fake_tap_mirror['id'],
            '--name', self._new_name,
        ]
        verify_list = [('name', self._new_name)]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        columns, data = self.cmd.take_action(parsed_args)
        attrs = {'name': self._new_name}

        mock_update_tap_m = self.app.client_manager.network.update_tap_mirror
        mock_update_tap_m.assert_called_once_with(
            fake_tap_mirror['id'], **attrs)
        self.assertEqual(self.columns, columns)
        fake_data = _get_data(
            new_tap_mirror,
            osc_tap_mirror._get_columns(new_tap_mirror)[1])
        self.assertItemEqual(fake_data, data)
