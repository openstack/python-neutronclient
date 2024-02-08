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

from neutronclient.osc.v2.sfc import sfc_flow_classifier
from neutronclient.tests.unit.osc.v2.sfc import fakes


class TestCreateSfcFlowClassifier(fakes.TestNeutronClientOSCV2):

    _fc = fakes.FakeSfcFlowClassifier.create_flow_classifier()

    columns = ('Description',
               'Destination IP',
               'Destination Port Range Max',
               'Destination Port Range Min',
               'Ethertype',
               'ID',
               'L7 Parameters',
               'Logical Destination Port',
               'Logical Source Port',
               'Name',
               'Project',
               'Protocol',
               'Source IP',
               'Source Port Range Max',
               'Source Port Range Min',
               'Summary',)

    def get_data(self):
        return (
            self._fc['description'],
            self._fc['destination_ip_prefix'],
            self._fc['destination_port_range_max'],
            self._fc['destination_port_range_min'],
            self._fc['ethertype'],
            self._fc['id'],
            self._fc['l7_parameters'],
            self._fc['logical_destination_port'],
            self._fc['logical_source_port'],
            self._fc['name'],
            self._fc['project_id'],
            self._fc['protocol'],
            self._fc['source_ip_prefix'],
            self._fc['source_port_range_max'],
            self._fc['source_port_range_min']
        )

    def setUp(self):
        super(TestCreateSfcFlowClassifier, self).setUp()
        self.network.create_sfc_flow_classifier = mock.Mock(
            return_value=self._fc)
        self.data = self.get_data()

        # Get the command object to test
        self.cmd = sfc_flow_classifier.CreateSfcFlowClassifier(self.app,
                                                               self.namespace)

    def test_create_flow_classifier_default_options(self):
        arglist = [
            "--logical-source-port", self._fc['logical_source_port'],
            "--ethertype", self._fc['ethertype'],
            self._fc['name'],
        ]
        verifylist = [
            ('logical_source_port', self._fc['logical_source_port']),
            ('ethertype', self._fc['ethertype']),
            ('name', self._fc['name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_sfc_flow_classifier.assert_called_once_with(
            **{'name': self._fc['name'],
               'logical_source_port': self._fc['logical_source_port'],
               'ethertype': self._fc['ethertype']
               }
        )
        self.assertEqual(self.columns, columns)

    def test_create_flow_classifier(self):
        arglist = [
            "--description", self._fc['description'],
            "--ethertype", self._fc['ethertype'],
            "--protocol", self._fc['protocol'],
            "--source-ip-prefix", self._fc['source_ip_prefix'],
            "--destination-ip-prefix", self._fc['destination_ip_prefix'],
            "--logical-source-port", self._fc['logical_source_port'],
            "--logical-destination-port", self._fc['logical_destination_port'],
            self._fc['name'],
            "--l7-parameters", 'url=path',
        ]

        param = 'url=path'

        verifylist = [
            ('description', self._fc['description']),
            ('name', self._fc['name']),
            ('ethertype', self._fc['ethertype']),
            ('protocol', self._fc['protocol']),
            ('source_ip_prefix', self._fc['source_ip_prefix']),
            ('destination_ip_prefix', self._fc['destination_ip_prefix']),
            ('logical_source_port', self._fc['logical_source_port']),
            ('logical_destination_port',
             self._fc['logical_destination_port']),
            ('l7_parameters', param)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))
        self.network.create_sfc_flow_classifier.assert_called_once_with(
            **{
                'name': self._fc['name'],
                'description': self._fc['description'],
                'ethertype': self._fc['ethertype'],
                'protocol': self._fc['protocol'],
                'source_ip_prefix': self._fc['source_ip_prefix'],
                'destination_ip_prefix': self._fc['destination_ip_prefix'],
                'logical_source_port': self._fc['logical_source_port'],
                'logical_destination_port':
                    self._fc['logical_destination_port'],
                'l7_parameters': param
            }
        )
        self.assertEqual(self.columns, columns)


class TestDeleteSfcFlowClassifier(fakes.TestNeutronClientOSCV2):

    _flow_classifier = \
        fakes.FakeSfcFlowClassifier.create_flow_classifiers(count=1)

    def setUp(self):
        super(TestDeleteSfcFlowClassifier, self).setUp()
        self.network.delete_sfc_flow_classifier = mock.Mock(
            return_value=None)
        self.cmd = sfc_flow_classifier.DeleteSfcFlowClassifier(self.app,
                                                               self.namespace)

    def test_delete_flow_classifier(self):
        client = self.app.client_manager.network
        mock_flow_classifier_delete = client.delete_sfc_flow_classifier
        arglist = [
            self._flow_classifier[0]['id'],
        ]
        verifylist = [
            ('flow_classifier', [self._flow_classifier[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        mock_flow_classifier_delete.assert_called_once_with(
            self._flow_classifier[0]['id'])
        self.assertIsNone(result)

    def test_delete_multiple_flow_classifiers_with_exception(self):
        client = self.app.client_manager.network
        target1 = self._flow_classifier[0]['id']
        arglist = [target1]
        verifylist = [('flow_classifier', [target1])]

        client.find_sfc_flow_classifier.side_effect = [
            target1, exceptions.CommandError
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        msg = "1 of 2 flow classifier(s) failed to delete."
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(msg, str(e))


class TestSetSfcFlowClassifier(fakes.TestNeutronClientOSCV2):
    _flow_classifier = fakes.FakeSfcFlowClassifier.create_flow_classifier()
    _flow_classifier_name = _flow_classifier['name']
    _flow_classifier_id = _flow_classifier['id']

    def setUp(self):
        super(TestSetSfcFlowClassifier, self).setUp()
        self.network.update_sfc_flow_classifier = mock.Mock(
            return_value=None)
        self.cmd = sfc_flow_classifier.SetSfcFlowClassifier(self.app,
                                                            self.namespace)

    def test_set_flow_classifier(self):
        client = self.app.client_manager.network
        mock_flow_classifier_update = client.update_sfc_flow_classifier
        arglist = [
            self._flow_classifier_name,
            '--name', 'name_updated',
            '--description', 'desc_updated'
        ]
        verifylist = [
            ('flow_classifier', self._flow_classifier_name),
            ('name', 'name_updated'),
            ('description', 'desc_updated'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': 'name_updated',
            'description': 'desc_updated'}
        mock_flow_classifier_update.assert_called_once_with(
            self._flow_classifier_name, **attrs)
        self.assertIsNone(result)


class TestShowSfcFlowClassifier(fakes.TestNeutronClientOSCV2):

    _fc = fakes.FakeSfcFlowClassifier.create_flow_classifier()
    data = (
        _fc['description'],
        _fc['destination_ip_prefix'],
        _fc['destination_port_range_max'],
        _fc['destination_port_range_min'],
        _fc['ethertype'],
        _fc['id'],
        _fc['l7_parameters'],
        _fc['logical_destination_port'],
        _fc['logical_source_port'],
        _fc['name'],
        _fc['project_id'],
        _fc['protocol'],
        _fc['source_ip_prefix'],
        _fc['source_port_range_max'],
        _fc['source_port_range_min']
    )
    _flow_classifier = _fc
    _flow_classifier_id = _fc['id']
    columns = ('Description',
               'Destination IP',
               'Destination Port Range Max',
               'Destination Port Range Min',
               'Ethertype',
               'ID',
               'L7 Parameters',
               'Logical Destination Port',
               'Logical Source Port',
               'Name',
               'Project',
               'Protocol',
               'Source IP',
               'Source Port Range Max',
               'Source Port Range Min',
               'Summary',)

    def setUp(self):
        super(TestShowSfcFlowClassifier, self).setUp()
        self.network.get_sfc_flow_classifier = mock.Mock(
            return_value=self._flow_classifier
        )
        # Get the command object to test
        self.cmd = sfc_flow_classifier.ShowSfcFlowClassifier(self.app,
                                                             self.namespace)

    def test_show_flow_classifier(self):
        client = self.app.client_manager.network
        mock_flow_classifier_show = client.get_sfc_flow_classifier
        arglist = [
            self._flow_classifier_id,
        ]
        verifylist = [
            ('flow_classifier', self._flow_classifier_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        mock_flow_classifier_show.assert_called_once_with(
            self._flow_classifier_id)
        self.assertEqual(self.columns, columns)


class TestListSfcFlowClassifier(fakes.TestNeutronClientOSCV2):

    _fc = fakes.FakeSfcFlowClassifier.create_flow_classifiers(count=1)

    columns = ('ID', 'Name', 'Summary')

    columns_long = ('ID', 'Name', 'Protocol', 'Ethertype', 'Source IP',
                    'Destination IP', 'Logical Source Port',
                    'Logical Destination Port', 'Source Port Range Min',
                    'Source Port Range Max', 'Destination Port Range Min',
                    'Destination Port Range Max', 'L7 Parameters',
                    'Description', 'Project')
    _flow_classifier = _fc[0]
    data = [
        _flow_classifier['id'],
        _flow_classifier['name'],
        _flow_classifier['protocol'],
        _flow_classifier['source_ip_prefix'],
        _flow_classifier['destination_ip_prefix'],
        _flow_classifier['logical_source_port'],
        _flow_classifier['logical_destination_port']
    ]
    data_long = [
        _flow_classifier['id'],
        _flow_classifier['name'],
        _flow_classifier['protocol'],
        _flow_classifier['ethertype'],
        _flow_classifier['source_ip_prefix'],
        _flow_classifier['destination_ip_prefix'],
        _flow_classifier['logical_source_port'],
        _flow_classifier['logical_destination_port'],
        _flow_classifier['source_port_range_min'],
        _flow_classifier['source_port_range_max'],
        _flow_classifier['destination_port_range_min'],
        _flow_classifier['destination_port_range_max'],
        _flow_classifier['l7_parameters'],
        _flow_classifier['description']
    ]

    _flow_classifier1 = {'flow_classifiers': _flow_classifier}
    _flow_classifier_id = _flow_classifier['id']

    def setUp(self):
        super(TestListSfcFlowClassifier, self).setUp()
        self.network.sfc_flow_classifiers = mock.Mock(
            return_value=self._fc
        )
        # Get the command object to test
        self.cmd = sfc_flow_classifier.ListSfcFlowClassifier(self.app,
                                                             self.namespace)

    def test_list_flow_classifiers(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns = self.cmd.take_action(parsed_args)
        fcs = self.network.sfc_flow_classifiers()
        fc = fcs[0]
        data = [
            fc['id'],
            fc['name'],
            fc['protocol'],
            fc['source_ip_prefix'],
            fc['destination_ip_prefix'],
            fc['logical_source_port'],
            fc['logical_destination_port']
        ]
        self.assertEqual(list(self.columns), columns[0])
        self.assertEqual(self.data, data)

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        fcs = self.network.sfc_flow_classifiers()
        fc = fcs[0]
        data = [
            fc['id'],
            fc['name'],
            fc['protocol'],
            fc['ethertype'],
            fc['source_ip_prefix'],
            fc['destination_ip_prefix'],
            fc['logical_source_port'],
            fc['logical_destination_port'],
            fc['source_port_range_min'],
            fc['source_port_range_max'],
            fc['destination_port_range_min'],
            fc['destination_port_range_max'],
            fc['l7_parameters'],
            fc['description']
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns_long = self.cmd.take_action(parsed_args)[0]
        self.assertEqual(list(self.columns_long), columns_long)
        self.assertEqual(self.data_long, data)
