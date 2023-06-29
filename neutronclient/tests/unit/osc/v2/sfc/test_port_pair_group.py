# Copyright (c) 2017 Huawei Technologies India Pvt.Limited.
# All Rights Reserved.
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

from unittest import mock

from osc_lib import exceptions
import testtools

from neutronclient.osc.v2.sfc import sfc_port_pair_group
from neutronclient.tests.unit.osc.v2.sfc import fakes


class TestCreateSfcPortPairGroup(fakes.TestNeutronClientOSCV2):

    _port_pair_group = fakes.FakeSfcPortPairGroup.create_port_pair_group()

    columns = ('Description',
               'ID',
               'Name',
               'Port Pair',
               'Port Pair Group Parameters',
               'Project',
               'Tap Enabled')

    def get_data(self, ppg):
        return (
            ppg['description'],
            ppg['id'],
            ppg['name'],
            ppg['port_pairs'],
            ppg['port_pair_group_parameters'],
            ppg['project_id'],
            ppg['tap_enabled']
        )

    def setUp(self):
        super(TestCreateSfcPortPairGroup, self).setUp()
        self.network.create_sfc_port_pair_group = mock.Mock(
            return_value=self._port_pair_group)
        self.data = self.get_data(self._port_pair_group)

        # Get the command object to test
        self.cmd = sfc_port_pair_group.CreateSfcPortPairGroup(self.app,
                                                              self.namespace)

    def test_create_port_pair_group_default_options(self):
        arglist = [
            "--port-pair", self._port_pair_group['port_pairs'],
            self._port_pair_group['name'],
        ]
        verifylist = [
            ('port_pairs', [self._port_pair_group['port_pairs']]),
            ('name', self._port_pair_group['name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))
        self.network.create_sfc_port_pair_group.assert_called_once_with(
            **{'name': self._port_pair_group['name'],
               'port_pairs': [self._port_pair_group['port_pairs']]})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_port_pair_group(self):
        arglist = [
            "--description", self._port_pair_group['description'],
            "--port-pair", self._port_pair_group['port_pairs'],
            self._port_pair_group['name'],
        ]
        verifylist = [
            ('port_pairs', [self._port_pair_group['port_pairs']]),
            ('name', self._port_pair_group['name']),
            ('description', self._port_pair_group['description']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_port_pair_group.assert_called_once_with(
            **{
                'name': self._port_pair_group['name'],
                'port_pairs': [self._port_pair_group['port_pairs']],
                'description': self._port_pair_group['description']})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_tap_enabled_port_pair_group(self):
        arglist = [
            "--description", self._port_pair_group['description'],
            "--port-pair", self._port_pair_group['port_pairs'],
            self._port_pair_group['name'],
            "--enable-tap"
        ]
        verifylist = [
            ('port_pairs', [self._port_pair_group['port_pairs']]),
            ('name', self._port_pair_group['name']),
            ('description', self._port_pair_group['description']),
            ('enable_tap', True)
        ]

        expected_data = self._update_expected_response_data(
            data={
                'tap_enabled': True
            }
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_port_pair_group.assert_called_once_with(
            **{
                'name': self._port_pair_group['name'],
                'port_pairs': [self._port_pair_group['port_pairs']],
                'description': self._port_pair_group['description'],
                'tap_enabled': True})
        self.assertEqual(self.columns, columns)
        self.assertEqual(expected_data, data)

    def _update_expected_response_data(self, data):
        # REVISIT(vks1) - This method can be common for other test functions.
        ppg = fakes.FakeSfcPortPairGroup.create_port_pair_group(data)
        self.network.create_sfc_port_pair_group.return_value = ppg
        return self.get_data(ppg)


class TestDeleteSfcPortPairGroup(fakes.TestNeutronClientOSCV2):

    _port_pair_group = (fakes.FakeSfcPortPairGroup.create_port_pair_groups
                        (count=1))

    def setUp(self):
        super(TestDeleteSfcPortPairGroup, self).setUp()
        self.network.delete_sfc_port_pair_group = mock.Mock(
            return_value=None)
        self.cmd = sfc_port_pair_group.DeleteSfcPortPairGroup(self.app,
                                                              self.namespace)

    def test_delete_port_pair_group(self):
        client = self.app.client_manager.network
        mock_port_pair_group_delete = client.delete_sfc_port_pair_group
        arglist = [
            self._port_pair_group[0]['id'],
        ]
        verifylist = [
            ('port_pair_group', [self._port_pair_group[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_port_pair_group_delete.assert_called_once_with(
            self._port_pair_group[0]['id'])
        self.assertIsNone(result)

    def test_delete_multiple_port_pair_groups_with_exception(self):
        client = self.app.client_manager.network
        target1 = 'target'
        arglist = [target1]
        verifylist = [('port_pair_group', [target1])]

        client.find_sfc_port_pair_group.side_effect = [
            target1, exceptions.CommandError
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        msg = "1 of 2 port pair group(s) failed to delete."
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestListSfcPortPairGroup(fakes.TestNeutronClientOSCV2):
    _ppgs = fakes.FakeSfcPortPairGroup.create_port_pair_groups(count=1)
    columns = ('ID', 'Name', 'Port Pair', 'Port Pair Group Parameters',
               'Tap Enabled')
    columns_long = ('ID', 'Name', 'Port Pair', 'Port Pair Group Parameters',
                    'Description', 'Project', 'Tap Enabled')
    _port_pair_group = _ppgs[0]
    data = [
        _port_pair_group['id'],
        _port_pair_group['name'],
        _port_pair_group['port_pairs'],
        _port_pair_group['port_pair_group_parameters'],
        _port_pair_group['tap_enabled']
    ]
    data_long = [
        _port_pair_group['id'],
        _port_pair_group['name'],
        _port_pair_group['port_pairs'],
        _port_pair_group['port_pair_group_parameters'],
        _port_pair_group['description'],
        _port_pair_group['tap_enabled']
    ]
    _port_pair_group1 = {'port_pair_groups': _port_pair_group}
    _port_pair_id = _port_pair_group['id']

    def setUp(self):
        super(TestListSfcPortPairGroup, self).setUp()

        self.network.sfc_port_pair_groups = mock.Mock(
            return_value=self._ppgs
        )
        # Get the command object to test
        self.cmd = sfc_port_pair_group.ListSfcPortPairGroup(self.app,
                                                            self.namespace)

    def test_list_port_pair_groups(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        ppgs = self.network.sfc_port_pair_groups()
        ppg = ppgs[0]
        data = [
            ppg['id'],
            ppg['name'],
            ppg['port_pairs'],
            ppg['port_pair_group_parameters'],
            ppg['tap_enabled']
        ]
        self.assertEqual(list(self.columns), columns)
        self.assertEqual(self.data, data)

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        ppgs = self.network.sfc_port_pair_groups()
        ppg = ppgs[0]
        data = [
            ppg['id'],
            ppg['name'],
            ppg['port_pairs'],
            ppg['port_pair_group_parameters'],
            ppg['description'],
            ppg['tap_enabled']
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns_long = self.cmd.take_action(parsed_args)[0]
        self.assertEqual(list(self.columns_long), columns_long)
        self.assertEqual(self.data_long, data)


class TestSetSfcPortPairGroup(fakes.TestNeutronClientOSCV2):
    _port_pair_group = fakes.FakeSfcPortPairGroup.create_port_pair_group()
    resource = _port_pair_group
    res = 'port_pair_group'
    _port_pair_group_name = _port_pair_group['name']
    ppg_pp = _port_pair_group['port_pairs']
    _port_pair_group_id = _port_pair_group['id']

    def setUp(self):
        super(TestSetSfcPortPairGroup, self).setUp()

        self.network.update_sfc_port_pair_group = mock.Mock(
            return_value=None)
        self.mocked = self.network.update_sfc_port_pair_group
        self.cmd = sfc_port_pair_group.SetSfcPortPairGroup(self.app,
                                                           self.namespace)

    def test_set_port_pair_group(self):
        target = self.resource['id']
        port_pair1 = 'additional_port1'
        port_pair2 = 'additional_port2'

        self.network.find_sfc_port_pair = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id}
        )
        self.network.find_sfc_port_pair_group = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id, 'port_pairs': self.ppg_pp}
        )

        arglist = [
            target,
            '--port-pair', port_pair1,
            '--port-pair', port_pair2,
        ]
        verifylist = [
            (self.res, target),
            ('port_pairs', [port_pair1, port_pair2])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'port_pairs': sorted([*self.ppg_pp, port_pair1, port_pair2])}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_set_no_port_pair(self):
        client = self.app.client_manager.network
        mock_port_pair_group_update = client.update_sfc_port_pair_group
        arglist = [
            self._port_pair_group_name,
            '--name', 'name_updated',
            '--description', 'desc_updated',
            '--no-port-pair',
        ]
        verifylist = [
            ('port_pair_group', self._port_pair_group_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
            ('no_port_pair', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'name': 'name_updated', 'description': 'desc_updated',
                 'port_pairs': []}
        mock_port_pair_group_update.assert_called_once_with(
            self._port_pair_group_name, **attrs)
        self.assertIsNone(result)


class TestShowSfcPortPairGroup(fakes.TestNeutronClientOSCV2):

    _ppg = fakes.FakeSfcPortPairGroup.create_port_pair_group()
    data = (
        _ppg['description'],
        _ppg['id'],
        _ppg['name'],
        _ppg['port_pairs'],
        _ppg['port_pair_group_parameters'],
        _ppg['project_id'],
        _ppg['tap_enabled'])
    _port_pair_group = _ppg
    _port_pair_group_id = _ppg['id']
    columns = (
        'Description',
        'ID',
        'Name',
        'Port Pair',
        'Port Pair Group Parameters',
        'Project',
        'Tap Enabled'
    )

    def setUp(self):
        super(TestShowSfcPortPairGroup, self).setUp()

        self.network.get_sfc_port_pair_group = mock.Mock(
            return_value=self._port_pair_group
        )
        self.cmd = sfc_port_pair_group.ShowSfcPortPairGroup(self.app,
                                                            self.namespace)

    def test_show_port_pair_group(self):
        client = self.app.client_manager.network
        mock_port_pair_group_show = client.get_sfc_port_pair_group
        arglist = [
            self._port_pair_group_id,
        ]
        verifylist = [
            ('port_pair_group', self._port_pair_group_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_port_pair_group_show.assert_called_once_with(
            self._port_pair_group_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestUnsetSfcPortPairGroup(fakes.TestNeutronClientOSCV2):
    _port_pair_group = fakes.FakeSfcPortPairGroup.create_port_pair_group()
    resource = _port_pair_group
    res = 'port_pair_group'
    _port_pair_group_name = _port_pair_group['name']
    _port_pair_group_id = _port_pair_group['id']
    ppg_pp = _port_pair_group['port_pairs']

    def setUp(self):
        super(TestUnsetSfcPortPairGroup, self).setUp()
        self.network.update_sfc_port_pair_group = mock.Mock(
            return_value=None)
        self.mocked = self.network.update_sfc_port_pair_group
        self.cmd = sfc_port_pair_group.UnsetSfcPortPairGroup(
            self.app, self.namespace)

    def test_unset_port_pair(self):
        target = self.resource['id']
        port_pair1 = 'additional_port1'
        port_pair2 = 'additional_port2'

        self.network.find_sfc_port_pair = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id}
        )
        self.network.find_sfc_port_pair_group = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id, 'port_pairs': self.ppg_pp}
        )
        arglist = [
            target,
            '--port-pair', port_pair1,
            '--port-pair', port_pair2,
        ]
        verifylist = [
            (self.res, target),
            ('port_pairs', [port_pair1, port_pair2])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'port_pairs': sorted([*self.ppg_pp])}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_unset_all_port_pair(self):
        client = self.app.client_manager.network
        mock_port_pair_group_update = client.update_sfc_port_pair_group
        arglist = [
            self._port_pair_group_name,
            '--all-port-pair',
        ]
        verifylist = [
            ('port_pair_group', self._port_pair_group_name),
            ('all_port_pair', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'port_pairs': []}
        mock_port_pair_group_update.assert_called_once_with(
            self._port_pair_group_name, **attrs)
        self.assertIsNone(result)
