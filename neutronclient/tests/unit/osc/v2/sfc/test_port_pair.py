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

from neutronclient.osc.v2.sfc import sfc_port_pair
from neutronclient.tests.unit.osc.v2.sfc import fakes


class TestCreateSfcPortPair(fakes.TestNeutronClientOSCV2):
    # The new port_pair created
    _port_pair = fakes.FakeSfcPortPair.create_port_pair()

    columns = ('Description',
               'Egress Logical Port',
               'ID',
               'Ingress Logical Port',
               'Name',
               'Project',
               'Service Function Parameters')

    def get_data(self):
        return (
            self._port_pair['description'],
            self._port_pair['egress'],
            self._port_pair['id'],
            self._port_pair['ingress'],
            self._port_pair['name'],
            self._port_pair['project_id'],
            self._port_pair['service_function_parameters']
        )

    def setUp(self):
        super(TestCreateSfcPortPair, self).setUp()
        self.network.create_sfc_port_pair = mock.Mock(
            return_value=self._port_pair)
        self.data = self.get_data()

        # Get the command object to test
        self.cmd = sfc_port_pair.CreateSfcPortPair(self.app, self.namespace)

    def test_create_port_pair_default_options(self):
        arglist = [
            "--ingress", self._port_pair['ingress'],
            "--egress", self._port_pair['egress'],
            self._port_pair['name'],
        ]
        verifylist = [
            ('ingress', self._port_pair['ingress']),
            ('egress', self._port_pair['egress']),
            ('name', self._port_pair['name'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_port_pair.assert_called_once_with(
            **{'name': self._port_pair['name'],
               'ingress': self._port_pair['ingress'],
               'egress': self._port_pair['egress']}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def _test_create_port_pair_all_options(self, correlation):
        arglist = [
            "--description", self._port_pair['description'],
            "--egress", self._port_pair['egress'],
            "--ingress", self._port_pair['ingress'],
            self._port_pair['name'],
            "--service-function-parameters",
            'correlation=%s,weight=1' % correlation,
        ]

        verifylist = [
            ('ingress', self._port_pair['ingress']),
            ('egress', self._port_pair['egress']),
            ('name', self._port_pair['name']),
            ('description', self._port_pair['description']),
            ('service_function_parameters',
             [{'correlation': correlation, 'weight': '1'}])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        if correlation == "None":
            correlation_param = None
        else:
            correlation_param = correlation
        self.network.create_sfc_port_pair.assert_called_once_with(
            **{'name': self._port_pair['name'],
               'ingress': self._port_pair['ingress'],
               'egress': self._port_pair['egress'],
               'description': self._port_pair['description'],
               'service_function_parameters':
                   {'correlation': correlation_param, 'weight': '1'}}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_port_pair_all_options(self):
        self._test_create_port_pair_all_options('None')

    def test_create_port_pair_all_options_mpls(self):
        self._test_create_port_pair_all_options('mpls')


class TestDeleteSfcPortPair(fakes.TestNeutronClientOSCV2):

    _port_pair = fakes.FakeSfcPortPair.create_port_pairs(count=1)

    def setUp(self):
        super(TestDeleteSfcPortPair, self).setUp()
        self.network.delete_sfc_port_pair = mock.Mock(return_value=None)
        self.cmd = sfc_port_pair.DeleteSfcPortPair(self.app, self.namespace)

    def test_delete_port_pair(self):
        client = self.app.client_manager.network
        mock_port_pair_delete = client.delete_sfc_port_pair
        arglist = [
            self._port_pair[0]['id'],
        ]
        verifylist = [
            ('port_pair', [self._port_pair[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_port_pair_delete.assert_called_once_with(
            self._port_pair[0]['id'])
        self.assertIsNone(result)

    def test_delete_multiple_port_pairs_with_exception(self):
        client = self.app.client_manager.network
        target1 = self._port_pair[0]['id']
        arglist = [target1]
        verifylist = [('port_pair', [target1])]

        client.find_sfc_port_pair.side_effect = [
            target1, exceptions.CommandError
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        msg = "1 of 2 port pair(s) failed to delete."
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestListSfcPortPair(fakes.TestNeutronClientOSCV2):
    _port_pairs = fakes.FakeSfcPortPair.create_port_pairs()
    columns = ('ID', 'Name', 'Ingress Logical Port', 'Egress Logical Port')
    columns_long = ('ID', 'Name', 'Ingress Logical Port',
                    'Egress Logical Port', 'Service Function Parameters',
                    'Description', 'Project')
    _port_pair = _port_pairs[0]
    data = [
        _port_pair['id'],
        _port_pair['name'],
        _port_pair['ingress'],
        _port_pair['egress']
    ]
    data_long = [
        _port_pair['id'],
        _port_pair['name'],
        _port_pair['ingress'],
        _port_pair['egress'],
        _port_pair['service_function_parameters'],
        _port_pair['description']
    ]
    _port_pair1 = {'port_pairs': _port_pair}
    _port_pair_id = _port_pair['id'],

    def setUp(self):
        super(TestListSfcPortPair, self).setUp()
        self.network.sfc_port_pairs = mock.Mock(
            return_value=self._port_pairs)
        # Get the command object to test
        self.cmd = sfc_port_pair.ListSfcPortPair(self.app, self.namespace)

    def test_list_port_pairs(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        port_pairs = self.network.sfc_port_pairs()
        port_pair = port_pairs[0]
        data = [
            port_pair['id'],
            port_pair['name'],
            port_pair['ingress'],
            port_pair['egress']
        ]
        self.assertEqual(list(self.columns), columns)
        self.assertEqual(self.data, data)

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        port_pairs = self.network.sfc_port_pairs()
        port_pair = port_pairs[0]
        data = [
            port_pair['id'],
            port_pair['name'],
            port_pair['ingress'],
            port_pair['egress'],
            port_pair['service_function_parameters'],
            port_pair['description']
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns_long = self.cmd.take_action(parsed_args)[0]
        self.assertEqual(list(self.columns_long), columns_long)
        self.assertEqual(self.data_long, data)


class TestSetSfcPortPair(fakes.TestNeutronClientOSCV2):
    _port_pair = fakes.FakeSfcPortPair.create_port_pair()
    _port_pair_name = _port_pair['name']
    _port_pair_id = _port_pair['id']

    def setUp(self):
        super(TestSetSfcPortPair, self).setUp()
        self.network.update_sfc_port_pair = mock.Mock(return_value=None)
        self.cmd = sfc_port_pair.SetSfcPortPair(self.app, self.namespace)

    def test_set_port_pair(self):
        client = self.app.client_manager.network
        mock_port_pair_update = client.update_sfc_port_pair
        arglist = [
            self._port_pair_name,
            '--name', 'name_updated',
            '--description', 'desc_updated'
        ]
        verifylist = [
            ('port_pair', self._port_pair_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': 'name_updated',
            'description': 'desc_updated'
        }
        mock_port_pair_update.assert_called_once_with(self._port_pair_name,
                                                      **attrs)
        self.assertIsNone(result)


class TestShowSfcPortPair(fakes.TestNeutronClientOSCV2):

    _pp = fakes.FakeSfcPortPair.create_port_pair()

    data = (
        _pp['description'],
        _pp['egress'],
        _pp['id'],
        _pp['ingress'],
        _pp['name'],
        _pp['project_id'],
        _pp['service_function_parameters'],
    )
    _port_pair = _pp
    _port_pair_id = _pp['id']
    columns = (
        'Description',
        'Egress Logical Port',
        'ID',
        'Ingress Logical Port',
        'Name',
        'Project',
        'Service Function Parameters'
    )

    def setUp(self):
        super(TestShowSfcPortPair, self).setUp()

        self.network.get_sfc_port_pair = mock.Mock(
            return_value=self._port_pair
        )

        # Get the command object to test
        self.cmd = sfc_port_pair.ShowSfcPortPair(self.app, self.namespace)

    def test_show_port_pair(self):
        client = self.app.client_manager.network
        mock_port_pair_show = client.get_sfc_port_pair
        arglist = [
            self._port_pair_id,
        ]
        verifylist = [
            ('port_pair', self._port_pair_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_port_pair_show.assert_called_once_with(self._port_pair_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
