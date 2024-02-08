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

from neutronclient.osc.v2.sfc import sfc_port_chain
from neutronclient.tests.unit.osc.v2.sfc import fakes


def _get_id(client, id_or_name, resource):
    return id_or_name


class TestCreateSfcPortChain(fakes.TestNeutronClientOSCV2):
    # The new port_chain created
    _port_chain = fakes.FakeSfcPortChain.create_port_chain()

    columns = ('Chain Parameters',
               'Description',
               'Flow Classifiers',
               'ID',
               'Name',
               'Port Pair Groups',
               'Project')

    def get_data(self):
        return (
            self._port_chain['chain_parameters'],
            self._port_chain['description'],
            self._port_chain['flow_classifiers'],
            self._port_chain['id'],
            self._port_chain['name'],
            self._port_chain['port_pair_groups'],
            self._port_chain['project_id'],
        )

    def setUp(self):
        super(TestCreateSfcPortChain, self).setUp()
        self.network.create_sfc_port_chain = mock.Mock(
            return_value=self._port_chain)
        self.data = self.get_data()

        # Get the command object to test
        self.cmd = sfc_port_chain.CreateSfcPortChain(self.app, self.namespace)

    def test_create_port_chain_default_options(self):
        arglist = [
            self._port_chain['name'],
            "--port-pair-group", self._port_chain['port_pair_groups']
        ]
        verifylist = [
            ('name', self._port_chain['name']),
            ('port_pair_groups', [self._port_chain['port_pair_groups']]),
            ('flow_classifiers', []),
            ('chain_parameters', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_port_chain.assert_called_once_with(
            **{
                'name': self._port_chain['name'],
                'port_pair_groups': [self._port_chain['port_pair_groups']]
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_port_chain_all_options(self):
        arglist = [
            "--description", self._port_chain['description'],
            "--port-pair-group", self._port_chain['port_pair_groups'],
            self._port_chain['name'],
            "--flow-classifier", self._port_chain['flow_classifiers'],
            "--chain-parameters", 'correlation=mpls,symmetric=true',
        ]

        cp = {'correlation': 'mpls', 'symmetric': 'true'}

        verifylist = [
            ('port_pair_groups', [self._port_chain['port_pair_groups']]),
            ('name', self._port_chain['name']),
            ('description', self._port_chain['description']),
            ('flow_classifiers', [self._port_chain['flow_classifiers']]),
            ('chain_parameters', [cp])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_port_chain.assert_called_once_with(
            **{
                'name': self._port_chain['name'],
                'port_pair_groups': [self._port_chain['port_pair_groups']],
                'description': self._port_chain['description'],
                'flow_classifiers': [self._port_chain['flow_classifiers']],
                'chain_parameters': cp
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteSfcPortChain(fakes.TestNeutronClientOSCV2):

    _port_chain = fakes.FakeSfcPortChain.create_port_chains(count=1)

    def setUp(self):
        super(TestDeleteSfcPortChain, self).setUp()
        self.network.delete_sfc_port_chain = mock.Mock(return_value=None)
        self.cmd = sfc_port_chain.DeleteSfcPortChain(self.app, self.namespace)

    def test_delete_port_chain(self):
        client = self.app.client_manager.network
        mock_port_chain_delete = client.delete_sfc_port_chain
        arglist = [
            self._port_chain[0]['id'],
        ]
        verifylist = [
            ('port_chain', [self._port_chain[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_port_chain_delete.assert_called_once_with(
            self._port_chain[0]['id'])
        self.assertIsNone(result)

    def test_delete_multiple_port_chains_with_exception(self):
        client = self.app.client_manager.network
        target1 = self._port_chain[0]['id']
        arglist = [target1]
        verifylist = [('port_chain', [target1])]

        client.find_sfc_port_chain.side_effect = [
            target1, exceptions.CommandError
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        msg = "1 of 2 port chain(s) failed to delete."
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestListSfcPortChain(fakes.TestNeutronClientOSCV2):
    _port_chains = fakes.FakeSfcPortChain.create_port_chains(count=1)
    columns = ('ID', 'Name', 'Port Pair Groups', 'Flow Classifiers',
               'Chain Parameters')
    columns_long = ('ID', 'Name', 'Port Pair Groups', 'Flow Classifiers',
                    'Chain Parameters', 'Description', 'Project')
    _port_chain = _port_chains[0]
    data = [
        _port_chain['id'],
        _port_chain['name'],
        _port_chain['port_pair_groups'],
        _port_chain['flow_classifiers'],
        _port_chain['chain_parameters'],
    ]
    data_long = [
        _port_chain['id'],
        _port_chain['name'],
        _port_chain['project_id'],
        _port_chain['port_pair_groups'],
        _port_chain['flow_classifiers'],
        _port_chain['chain_parameters'],
        _port_chain['description']
    ]
    _port_chain1 = {'port_chains': _port_chain}
    _port_chain_id = _port_chain['id']

    def setUp(self):
        super(TestListSfcPortChain, self).setUp()
        self.network.sfc_port_chains = mock.Mock(
            return_value=self._port_chains
        )
        # Get the command object to test
        self.cmd = sfc_port_chain.ListSfcPortChain(self.app, self.namespace)

    def test_list_port_chains(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        pcs = self.network.sfc_port_chains()
        pc = pcs[0]
        data = [
            pc['id'],
            pc['name'],
            pc['port_pair_groups'],
            pc['flow_classifiers'],
            pc['chain_parameters'],
        ]
        self.assertEqual(list(self.columns), columns)
        self.assertEqual(self.data, data)

    def test_list_port_chain_with_long_opion(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        pcs = self.network.sfc_port_chains()
        pc = pcs[0]
        data = [
            pc['id'],
            pc['name'],
            pc['project_id'],
            pc['port_pair_groups'],
            pc['flow_classifiers'],
            pc['chain_parameters'],
            pc['description']
        ]
        self.assertEqual(list(self.columns_long), columns)
        self.assertEqual(self.data_long, data)


class TestSetSfcPortChain(fakes.TestNeutronClientOSCV2):
    _port_chain = fakes.FakeSfcPortChain.create_port_chain()
    resource = _port_chain
    res = 'port_chain'
    _port_chain_name = _port_chain['name']
    _port_chain_id = _port_chain['id']
    pc_ppg = _port_chain['port_pair_groups']
    pc_fc = _port_chain['flow_classifiers']

    def setUp(self):
        super(TestSetSfcPortChain, self).setUp()
        self.mocked = self.network.update_sfc_port_chain
        self.cmd = sfc_port_chain.SetSfcPortChain(self.app, self.namespace)

    def test_set_port_chain(self):
        client = self.app.client_manager.network
        mock_port_chain_update = client.update_sfc_port_chain
        arglist = [
            self._port_chain_name,
            '--name', 'name_updated',
            '--description', 'desc_updated',
        ]
        verifylist = [
            ('port_chain', self._port_chain_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {'name': 'name_updated', 'description': 'desc_updated'}
        mock_port_chain_update.assert_called_once_with(self._port_chain_name,
                                                       **attrs)
        self.assertIsNone(result)

    def test_set_flow_classifiers(self):
        target = self.resource['id']
        fc1 = 'flow_classifier1'
        fc2 = 'flow_classifier2'

        self.network.find_sfc_port_chain = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id, 'flow_classifiers': [self.pc_fc]}
        )
        self.network.find_sfc_flow_classifier.side_effect = \
            lambda name_or_id, ignore_missing=False: {'id': name_or_id}
        arglist = [
            target,
            '--flow-classifier', fc1,
            '--flow-classifier', fc2,
        ]
        verifylist = [
            (self.res, target),
            ('flow_classifiers', [fc1, fc2])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'flow_classifiers': [self.pc_fc, fc1, fc2]}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_set_no_flow_classifier(self):
        client = self.app.client_manager.network
        mock_port_chain_update = client.update_sfc_port_chain
        arglist = [
            self._port_chain_name,
            '--no-flow-classifier',
        ]
        verifylist = [
            ('port_chain', self._port_chain_name),
            ('no_flow_classifier', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {'flow_classifiers': []}
        mock_port_chain_update.assert_called_once_with(self._port_chain_name,
                                                       **attrs)
        self.assertIsNone(result)

    def test_set_port_pair_groups(self):
        target = self.resource['id']
        existing_ppg = self.pc_ppg
        ppg1 = 'port_pair_group1'
        ppg2 = 'port_pair_group2'

        self.network.find_sfc_port_chain = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id, 'port_pair_groups': [self.pc_ppg]}
        )
        arglist = [
            target,
            '--port-pair-group', ppg1,
            '--port-pair-group', ppg2,
        ]
        verifylist = [
            (self.res, target),
            ('port_pair_groups', [ppg1, ppg2])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'port_pair_groups': [existing_ppg, ppg1, ppg2]}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_set_no_port_pair_group(self):
        target = self.resource['id']
        ppg1 = 'port_pair_group1'

        arglist = [
            target,
            '--no-port-pair-group',
            '--port-pair-group', ppg1,
        ]
        verifylist = [
            (self.res, target),
            ('no_port_pair_group', True),
            ('port_pair_groups', [ppg1])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'port_pair_groups': [ppg1]}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_set_only_no_port_pair_group(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-port-pair-group',
        ]
        verifylist = [
            (self.res, target),
            ('no_port_pair_group', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


class TestShowSfcPortChain(fakes.TestNeutronClientOSCV2):

    _pc = fakes.FakeSfcPortChain.create_port_chain()
    data = (
        _pc['chain_parameters'],
        _pc['description'],
        _pc['flow_classifiers'],
        _pc['id'],
        _pc['name'],
        _pc['port_pair_groups'],
        _pc['project_id']
    )
    _port_chain = _pc
    _port_chain_id = _pc['id']
    columns = ('Chain Parameters',
               'Description',
               'Flow Classifiers',
               'ID',
               'Name',
               'Port Pair Groups',
               'Project')

    def setUp(self):
        super(TestShowSfcPortChain, self).setUp()
        self.network.get_sfc_port_chain = mock.Mock(
            return_value=self._port_chain
        )
        # Get the command object to test
        self.cmd = sfc_port_chain.ShowSfcPortChain(self.app, self.namespace)

    def test_show_port_chain(self):
        client = self.app.client_manager.network
        mock_port_chain_show = client.get_sfc_port_chain
        arglist = [
            self._port_chain_id,
        ]
        verifylist = [
            ('port_chain', self._port_chain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_port_chain_show.assert_called_once_with(self._port_chain_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestUnsetSfcPortChain(fakes.TestNeutronClientOSCV2):
    _port_chain = fakes.FakeSfcPortChain.create_port_chain()
    resource = _port_chain
    res = 'port_chain'
    _port_chain_name = _port_chain['name']
    _port_chain_id = _port_chain['id']
    pc_ppg = _port_chain['port_pair_groups']
    pc_fc = _port_chain['flow_classifiers']

    def setUp(self):
        super(TestUnsetSfcPortChain, self).setUp()
        self.network.update_sfc_port_chain = mock.Mock(
            return_value=None)
        self.mocked = self.network.update_sfc_port_chain
        self.cmd = sfc_port_chain.UnsetSfcPortChain(self.app, self.namespace)

    def test_unset_port_pair_group(self):
        target = self.resource['id']
        ppg1 = 'port_pair_group1'

        self.network.find_sfc_port_chain = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id, 'port_pair_groups': [self.pc_ppg]}
        )
        self.network.find_sfc_port_pair_group.side_effect = \
            lambda name_or_id, ignore_missing=False: {'id': name_or_id}

        arglist = [
            target,
            '--port-pair-group', ppg1,
        ]
        verifylist = [
            (self.res, target),
            ('port_pair_groups', [ppg1])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'port_pair_groups': [self.pc_ppg]}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_unset_flow_classifier(self):
        target = self.resource['id']
        fc1 = 'flow_classifier1'
        self.network.find_sfc_port_chain = mock.Mock(
            side_effect=lambda name_or_id, ignore_missing=False:
            {'id': name_or_id, 'flow_classifiers': [self.pc_fc]}
        )
        self.network.find_sfc_flow_classifier.side_effect = \
            lambda name_or_id, ignore_missing=False: {'id': name_or_id}

        arglist = [
            target,
            '--flow-classifier', fc1,
        ]
        verifylist = [
            (self.res, target),
            ('flow_classifiers', [fc1])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'flow_classifiers': [self.pc_fc]}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertIsNone(result)

    def test_unset_all_flow_classifier(self):
        client = self.app.client_manager.network
        target = self.resource['id']
        mock_port_chain_update = client.update_sfc_port_chain
        arglist = [
            target,
            '--all-flow-classifier',
        ]
        verifylist = [
            (self.res, target),
            ('all_flow_classifier', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expect = {'flow_classifiers': []}
        mock_port_chain_update.assert_called_once_with(target,
                                                       **expect)
        self.assertIsNone(result)
