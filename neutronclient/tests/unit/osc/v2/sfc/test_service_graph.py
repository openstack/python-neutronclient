# Copyright 2017 Intel Corporation.
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
from osc_lib.tests import utils as tests_utils
import testtools

from neutronclient.osc.v2.sfc import sfc_service_graph
from neutronclient.tests.unit.osc.v2.sfc import fakes


class TestListSfcServiceGraph(fakes.TestNeutronClientOSCV2):
    _service_graphs = fakes.FakeSfcServiceGraph.create_sfc_service_graphs(
        count=1)
    columns = ('ID', 'Name', 'Branching Points')
    columns_long = ('ID', 'Name', 'Branching Points', 'Description', 'Project')
    _service_graph = _service_graphs[0]
    data = [
        _service_graph['id'],
        _service_graph['name'],
        _service_graph['port_chains']
    ]
    data_long = [
        _service_graph['id'],
        _service_graph['name'],
        _service_graph['port_chains'],
        _service_graph['description'],
        _service_graph['project_id']
    ]
    _service_graph1 = {'service_graphs': _service_graph}
    _service_graph_id = _service_graph['id']

    def setUp(self):
        super(TestListSfcServiceGraph, self).setUp()
        self.network.sfc_service_graphs = mock.Mock(
            return_value=self._service_graphs
        )
        # Get the command object to test
        self.cmd = sfc_service_graph.ListSfcServiceGraph(
            self.app, self.namespace)

    def test_list_sfc_service_graphs(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        sgs = self.network.sfc_service_graphs()
        sg = sgs[0]
        data = [
            sg['id'],
            sg['name'],
            sg['port_chains']
        ]
        self.assertEqual(list(self.columns), columns)
        self.assertEqual(self.data, data)

    def test_list_sfc_service_graphs_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)[0]
        sgs = self.network.sfc_service_graphs()
        sg = sgs[0]
        data = [
            sg['id'],
            sg['name'],
            sg['port_chains'],
            sg['description'],
            sg['project_id']
        ]
        self.assertEqual(list(self.columns_long), columns)
        self.assertEqual(self.data_long, data)


class TestCreateSfcServiceGraph(fakes.TestNeutronClientOSCV2):
    _service_graph = fakes.FakeSfcServiceGraph.create_sfc_service_graph()

    columns = ('ID', 'Name', 'Branching Points')
    columns_long = ('Branching Points', 'Description', 'ID', 'Name', 'Project')

    def get_data(self):
        return (
            self._service_graph['port_chains'],
            self._service_graph['description'],
            self._service_graph['id'],
            self._service_graph['name'],
            self._service_graph['project_id'],
        )

    def setUp(self):
        super(TestCreateSfcServiceGraph, self).setUp()
        self.network.create_sfc_service_graph = mock.Mock(
            return_value=self._service_graph)
        self.data = self.get_data()
        self.cmd = sfc_service_graph.CreateSfcServiceGraph(
            self.app, self.namespace)

    def test_create_sfc_service_graph(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_sfc_service_graph_without_loop(self):
        bp1_str = 'pc1:pc2,pc3'
        bp2_str = 'pc2:pc4'
        self.cmd = sfc_service_graph.CreateSfcServiceGraph(
            self.app, self.namespace)

        arglist = [
            "--description", self._service_graph['description'],
            "--branching-point", bp1_str,
            "--branching-point", bp2_str,
            self._service_graph['name']]

        pcs = {'pc1': ['pc2', 'pc3'], 'pc2': ['pc4']}

        verifylist = [
            ("description", self._service_graph['description']),
            ("branching_points", [bp1_str, bp2_str]),
            ("name", self._service_graph['name'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_service_graph.assert_called_once_with(**{
                'description': self._service_graph['description'],
                'name': self._service_graph['name'],
                'port_chains': pcs
        })
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data, data)

    def test_create_sfc_service_graph_with_loop(self):
        bp1_str = 'pc1:pc2,pc3;'
        bp2_str = 'pc2:pc1'
        self.cmd = sfc_service_graph.CreateSfcServiceGraph(
            self.app, self.namespace)

        arglist = [
            "--description", self._service_graph['description'],
            "--branching-point", bp1_str,
            "--branching-point", bp2_str,
            self._service_graph['name']]

        verifylist = [
            ("description", self._service_graph['description']),
            ("branching_points", [bp1_str, bp2_str]),
            ("name", self._service_graph['name'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)

    def test_create_sfc_service_graph_invalid_port_chains(self):
        bp1_str = 'pc1:pc2,pc3:'
        self.cmd = sfc_service_graph.CreateSfcServiceGraph(
            self.app, self.namespace)

        arglist = [
            "--description", self._service_graph['description'],
            "--branching-point", bp1_str,
            self._service_graph['name']]

        verifylist = [
            ("description", self._service_graph['description']),
            ("branching_points", [bp1_str]),
            ("name", self._service_graph['name'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)

    def test_create_sfc_service_graph_duplicate_src_chains(self):
        bp1_str = 'pc1:pc2,pc3;'
        bp2_str = 'pc1:pc4'
        self.cmd = sfc_service_graph.CreateSfcServiceGraph(
            self.app, self.namespace)

        arglist = [
            "--description", self._service_graph['description'],
            "--branching-point", bp1_str,
            "--branching-point", bp2_str,
            self._service_graph['name']]

        verifylist = [
            ("description", self._service_graph['description']),
            ("branching_points", [bp1_str, bp2_str]),
            ("name", self._service_graph['name'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


class TestDeleteSfcServiceGraph(fakes.TestNeutronClientOSCV2):

    _service_graph = fakes.FakeSfcServiceGraph.create_sfc_service_graphs(
        count=1)

    def setUp(self):
        super(TestDeleteSfcServiceGraph, self).setUp()
        self.network.delete_sfc_service_graph = mock.Mock(
            return_value=None)
        self.cmd = sfc_service_graph.DeleteSfcServiceGraph(
            self.app, self.namespace)

    def test_delete_sfc_service_graph(self):
        client = self.app.client_manager.network
        mock_service_graph_delete = client.delete_sfc_service_graph
        arglist = [
            self._service_graph[0]['id'],
        ]
        verifylist = [
            ('service_graph', [self._service_graph[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_service_graph_delete.assert_called_once_with(
            self._service_graph[0]['id'])
        self.assertIsNone(result)

    def test_delete_multiple_service_graphs_with_exception(self):
        client = self.app.client_manager.network
        target = self._service_graph[0]['id']
        arglist = [target]
        verifylist = [('service_graph', [target])]

        client.find_sfc_service_graph.side_effect = [
            target, exceptions.CommandError
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        msg = "1 of 2 service graph(s) failed to delete."
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestShowSfcServiceGraph(fakes.TestNeutronClientOSCV2):

    _sg = fakes.FakeSfcServiceGraph.create_sfc_service_graph()
    columns = ('ID', 'Name', 'Branching Points')
    columns_long = ('Branching Points', 'Description', 'ID', 'Name', 'Project')
    data = (
        _sg['id'],
        _sg['name'],
        _sg['port_chains']
    )
    data_long = (
        _sg['port_chains'],
        _sg['description'],
        _sg['id'],
        _sg['name'],
        _sg['project_id']
    )

    _service_graph = _sg
    _service_graph_id = _sg['id']

    def setUp(self):
        super(TestShowSfcServiceGraph, self).setUp()
        self.network.get_sfc_service_graph = mock.Mock(
            return_value=self._service_graph
        )
        # Get the command object to test
        self.cmd = sfc_service_graph.ShowSfcServiceGraph(
            self.app, self.namespace)

    def test_service_graph_show(self):
        client = self.app.client_manager.network
        mock_service_graph_show = client.get_sfc_service_graph
        arglist = [
            self._service_graph_id,
        ]
        verifylist = [
            ('service_graph', self._service_graph_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_service_graph_show.assert_called_once_with(self._service_graph_id)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, data)


class TestSetSfcServiceGraph(fakes.TestNeutronClientOSCV2):
    _service_graph = fakes.FakeSfcServiceGraph.create_sfc_service_graph()
    _service_graph_name = _service_graph['name']
    _service_graph_id = _service_graph['id']

    def setUp(self):
        super(TestSetSfcServiceGraph, self).setUp()
        self.network.update_sfc_service_graph = mock.Mock(
            return_value=None)
        self.cmd = sfc_service_graph.SetSfcServiceGraph(
            self.app, self.namespace)

    def test_set_service_graph(self):
        client = self.app.client_manager.network
        mock_service_graph_update = client.update_sfc_service_graph
        arglist = [
            self._service_graph_name,
            '--name', 'name_updated',
            '--description', 'desc_updated'
        ]
        verifylist = [
            ('service_graph', self._service_graph_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': 'name_updated',
            'description': 'desc_updated'
        }
        mock_service_graph_update.assert_called_once_with(
            self._service_graph_name, **attrs)
        self.assertIsNone(result)
