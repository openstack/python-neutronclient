# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 ????
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
#    @author: Salvatore Orlando, Citrix Systems

""" Module containing unit tests for Quantum
    command line interface

"""


import logging
import sys
import unittest

from quantum import api as server
from quantum.client import cli_lib as cli
from quantum.client import Client
from quantum.db import api as db
from quantum.tests.unit.client_tools import stubs as client_stubs

LOG = logging.getLogger('quantum.tests.test_cli')
API_VERSION = "1.1"
FORMAT = 'json'


class CLITest(unittest.TestCase):

    def setUp(self):
        """Prepare the test environment"""
        options = {}
        options['plugin_provider'] = \
          'quantum.plugins.sample.SamplePlugin.FakePlugin'
        #TODO: make the version of the API router configurable
        self.api = server.APIRouterV11(options)

        self.tenant_id = "test_tenant"
        self.network_name_1 = "test_network_1"
        self.network_name_2 = "test_network_2"
        self.version = API_VERSION
        # Prepare client and plugin manager
        self.client = Client(tenant=self.tenant_id,
                             format=FORMAT,
                             testingStub=client_stubs.FakeHTTPConnection,
                             version=self.version)
        # Redirect stdout
        self.fake_stdout = client_stubs.FakeStdout()
        sys.stdout = self.fake_stdout

    def tearDown(self):
        """Clear the test environment"""
        db.clear_db()
        sys.stdout = sys.__stdout__

    def _verify_list_networks(self):
            # Verification - get raw result from db
            nw_list = db.network_list(self.tenant_id)
            networks = [{'id': nw.uuid, 'name': nw.name}
                         for nw in nw_list]
            # Fill CLI template
            output = cli.prepare_output('list_nets',
                                        self.tenant_id,
                                        dict(networks=networks),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_list_networks_details(self):
            # Verification - get raw result from db
            nw_list = db.network_list(self.tenant_id)
            networks = [dict(id=nw.uuid, name=nw.name) for nw in nw_list]
            # Fill CLI template
            output = cli.prepare_output('list_nets_detail',
                                        self.tenant_id,
                                        dict(networks=networks),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_create_network(self):
            # Verification - get raw result from db
            nw_list = db.network_list(self.tenant_id)
            if len(nw_list) != 1:
                self.fail("No network created")
            network_id = nw_list[0].uuid
            # Fill CLI template
            output = cli.prepare_output('create_net',
                                        self.tenant_id,
                                        dict(network_id=network_id),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_delete_network(self, network_id):
            # Verification - get raw result from db
            nw_list = db.network_list(self.tenant_id)
            if len(nw_list) != 0:
                self.fail("DB should not contain any network")
            # Fill CLI template
            output = cli.prepare_output('delete_net',
                                        self.tenant_id,
                                        dict(network_id=network_id),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_update_network(self):
            # Verification - get raw result from db
            nw_list = db.network_list(self.tenant_id)
            network_data = {'id': nw_list[0].uuid,
                            'name': nw_list[0].name,
                            'op-status': nw_list[0].op_status}
            # Fill CLI template
            output = cli.prepare_output('update_net',
                                        self.tenant_id,
                                        dict(network=network_data),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_show_network(self):
            # Verification - get raw result from db
            nw = db.network_list(self.tenant_id)[0]
            network = {'id': nw.uuid,
                       'name': nw.name,
                       'op-status': nw.op_status}
            # Fill CLI template
            output = cli.prepare_output('show_net',
                                        self.tenant_id,
                                        dict(network=network),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_show_network_details(self):
            # Verification - get raw result from db
            nw = db.network_list(self.tenant_id)[0]
            network = {'id': nw.uuid,
                       'name': nw.name,
                       'op-status': nw.op_status}
            port_list = db.port_list(nw.uuid)
            if not port_list:
                network['ports'] = [{'id': '<none>',
                                     'state': '<none>',
                                     'attachment': {'id': '<none>'}}]
            else:
                network['ports'] = []
                for port in port_list:
                    network['ports'].append({'id': port.uuid,
                                             'state': port.state,
                                             'attachment': {'id':
                                                            port.interface_id
                                                            or '<none>'}})

            # Fill CLI template
            output = cli.prepare_output('show_net_detail',
                                        self.tenant_id,
                                        dict(network=network),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_list_ports(self, network_id):
            # Verification - get raw result from db
            port_list = db.port_list(network_id)
            ports = [dict(id=port.uuid, state=port.state)
                     for port in port_list]
            # Fill CLI template
            output = cli.prepare_output('list_ports',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             ports=ports),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_list_ports_details(self, network_id):
            # Verification - get raw result from db
            port_list = db.port_list(network_id)
            ports = [dict(id=port.uuid, state=port.state)
                     for port in port_list]
            # Fill CLI template
            output = cli.prepare_output('list_ports_detail',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             ports=ports),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_create_port(self, network_id):
            # Verification - get raw result from db
            port_list = db.port_list(network_id)
            if len(port_list) != 1:
                self.fail("No port created")
            port_id = port_list[0].uuid
            # Fill CLI template
            output = cli.prepare_output('create_port',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port_id=port_id),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_delete_port(self, network_id, port_id):
            # Verification - get raw result from db
            port_list = db.port_list(network_id)
            if len(port_list) != 0:
                self.fail("DB should not contain any port")
            # Fill CLI template
            output = cli.prepare_output('delete_port',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port_id=port_id),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_update_port(self, network_id, port_id):
            # Verification - get raw result from db
            port = db.port_get(port_id, network_id)
            port_data = {'id': port.uuid,
                         'state': port.state,
                         'op-status': port.op_status}
            # Fill CLI template
            output = cli.prepare_output('update_port',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port=port_data),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_show_port(self, network_id, port_id):
            # Verification - get raw result from db
            port = db.port_get(port_id, network_id)
            port_data = {'id': port.uuid,
                         'state': port.state,
                         'attachment': {'id': port.interface_id or '<none>'},
                         'op-status': port.op_status}

            # Fill CLI template
            output = cli.prepare_output('show_port',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port=port_data),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_show_port_details(self, network_id, port_id):
            # Verification - get raw result from db
            # TODO(salvatore-orlando): Must resolve this issue with
            # attachment in separate bug fix.
            port = db.port_get(port_id, network_id)
            port_data = {'id': port.uuid,
                         'state': port.state,
                         'attachment': {'id': port.interface_id or '<none>'},
                         'op-status': port.op_status}

            # Fill CLI template
            output = cli.prepare_output('show_port_detail',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port=port_data),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_plug_iface(self, network_id, port_id):
            # Verification - get raw result from db
            port = db.port_get(port_id, network_id)
            # Fill CLI template
            output = cli.prepare_output("plug_iface",
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port_id=port['uuid'],
                                             attachment=port['interface_id']),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_unplug_iface(self, network_id, port_id):
            # Verification - get raw result from db
            port = db.port_get(port_id, network_id)
            # Fill CLI template
            output = cli.prepare_output("unplug_iface",
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port_id=port['uuid']),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def _verify_show_iface(self, network_id, port_id):
            # Verification - get raw result from db
            port = db.port_get(port_id, network_id)
            iface = {'id': port.interface_id or '<none>'}

            # Fill CLI template
            output = cli.prepare_output('show_iface',
                                        self.tenant_id,
                                        dict(network_id=network_id,
                                             port_id=port.uuid,
                                             iface=iface),
                                        self.version)
            # Verify!
            # Must add newline at the end to match effect of print call
            self.assertEquals(self.fake_stdout.make_string(), output + '\n')

    def test_list_networks_v10(self):
        try:
            # Pre-populate data for testing using db api
            db.network_create(self.tenant_id, self.network_name_1)
            db.network_create(self.tenant_id, self.network_name_2)

            cli.list_nets(self.client,
                          self.tenant_id,
                          self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_networks_v10 failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_networks()

    def test_list_networks_details_v10(self):
        try:
            # Pre-populate data for testing using db api
            db.network_create(self.tenant_id, self.network_name_1)
            db.network_create(self.tenant_id, self.network_name_2)

            cli.list_nets_detail(self.client,
                                 self.tenant_id,
                                 self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_networks_details_v10 failed due to" +
                      " an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_networks_details()

    def test_list_networks_v11(self):
        try:
            # Pre-populate data for testing using db api
            db.network_create(self.tenant_id, self.network_name_1)
            db.network_create(self.tenant_id, self.network_name_2)
            #TODO: test filters
            cli.list_nets_v11(self.client,
                              self.tenant_id,
                              self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_networks_v11 failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_networks()

    def test_list_networks_details_v11(self):
        try:
            # Pre-populate data for testing using db api
            db.network_create(self.tenant_id, self.network_name_1)
            db.network_create(self.tenant_id, self.network_name_2)
            #TODO: test filters
            cli.list_nets_detail_v11(self.client,
                                     self.tenant_id,
                                     self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_networks_details_v11 failed due to " +
                      "an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_networks_details()

    def test_create_network(self):
        try:
            cli.create_net(self.client,
                           self.tenant_id,
                           "test",
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_create_network failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_create_network()

    def test_delete_network(self):
        try:
            db.network_create(self.tenant_id, self.network_name_1)
            network_id = db.network_list(self.tenant_id)[0]['uuid']
            cli.delete_net(self.client,
                           self.tenant_id,
                           network_id,
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_delete_network failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_delete_network(network_id)

    def test_show_network(self):
        try:
            # Load some data into the datbase
            net = db.network_create(self.tenant_id, self.network_name_1)
            cli.show_net(self.client,
                         self.tenant_id,
                         net['uuid'],
                         self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_detail_network failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_network()

    def test_show_network_details_no_ports(self):
        try:
            # Load some data into the datbase
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            cli.show_net_detail(self.client,
                                self.tenant_id,
                                network_id,
                                self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_network_details_no_ports failed due to" +
                      " an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_network_details()

    def test_show_network_details(self):
        iface_id = "flavor crystals"
        try:
            # Load some data into the datbase
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            db.port_set_attachment(port_id, network_id, iface_id)
            port = db.port_create(network_id)
            cli.show_net_detail(self.client,
                                self.tenant_id,
                                network_id,
                                self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_network_details failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_network_details()

    def test_update_network(self):
        try:
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            cli.update_net(self.client,
                           self.tenant_id,
                           network_id,
                           'name=%s' % self.network_name_2,
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_update_network failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_update_network()

    def test_list_ports_v10(self):
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            db.port_create(network_id)
            db.port_create(network_id)
            cli.list_ports(self.client,
                           self.tenant_id,
                           network_id,
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_ports failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_ports(network_id)

    def test_list_ports_details_v10(self):
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            db.port_create(network_id)
            db.port_create(network_id)
            cli.list_ports_detail(self.client,
                                  self.tenant_id,
                                  network_id,
                                  self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_ports_details_v10 failed due to" +
                      " an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_ports_details(network_id)

    def test_list_ports_v11(self):
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            db.port_create(network_id)
            db.port_create(network_id)
            #TODO: test filters
            cli.list_ports_v11(self.client,
                               self.tenant_id,
                               network_id,
                               self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_ports_v11 failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_ports(network_id)

    def test_list_ports_details_v11(self):
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            db.port_create(network_id)
            db.port_create(network_id)
            #TODO: test filters
            cli.list_ports_detail_v11(self.client,
                                      self.tenant_id,
                                      network_id,
                                      self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_list_ports_details_v11 failed due to " +
                      "an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_list_ports_details(network_id)

    def test_create_port(self):
        network_id = None
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            cli.create_port(self.client,
                            self.tenant_id,
                            network_id,
                            self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_create_port failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_create_port(network_id)

    def test_delete_port(self):
        network_id = None
        port_id = None
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            cli.delete_port(self.client,
                            self.tenant_id,
                            network_id,
                            port_id,
                            self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_delete_port failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_delete_port(network_id, port_id)

    def test_update_port(self):
        try:
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            # Default state is DOWN - change to ACTIVE.
            cli.update_port(self.client,
                            self.tenant_id,
                            network_id,
                            port_id,
                            'state=ACTIVE',
                            self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_update_port failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_update_port(network_id, port_id)

    def test_show_port(self):
        network_id = None
        port_id = None
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            cli.show_port(self.client,
                          self.tenant_id,
                          network_id,
                          port_id,
                          self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_port failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_port(network_id, port_id)

    def test_show_port_details_no_attach(self):
        network_id = None
        port_id = None
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            cli.show_port_detail(self.client,
                                 self.tenant_id,
                                 network_id,
                                 port_id,
                                 self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_port_details_no_attach failed due to" +
                      " an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_port_details(network_id, port_id)

    def test_show_port_details_with_attach(self):
        network_id = None
        port_id = None
        iface_id = "flavor crystals"
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            db.port_set_attachment(port_id, network_id, iface_id)
            cli.show_port_detail(self.client,
                                 self.tenant_id,
                                 network_id,
                                 port_id,
                                 self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_port_details_with_attach failed due" +
                      " to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_port_details(network_id, port_id)

    def test_plug_iface(self):
        network_id = None
        port_id = None
        try:
            # Load some data into the datbase
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(net['uuid'])
            port_id = port['uuid']
            cli.plug_iface(self.client,
                           self.tenant_id,
                           network_id,
                           port_id,
                           "test_iface_id",
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_plug_iface failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_plug_iface(network_id, port_id)

    def test_unplug_iface(self):
        network_id = None
        port_id = None
        try:
            # Load some data into the datbase
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(net['uuid'])
            port_id = port['uuid']
            db.port_set_attachment(port_id, network_id, "test_iface_id")
            cli.unplug_iface(self.client,
                             self.tenant_id,
                             network_id,
                             port_id,
                             self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_plug_iface failed due to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_unplug_iface(network_id, port_id)

    def test_show_iface_no_attach(self):
        network_id = None
        port_id = None
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            cli.show_iface(self.client,
                           self.tenant_id,
                           network_id,
                           port_id,
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_iface_no_attach failed due to" +
                      " an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_iface(network_id, port_id)

    def test_show_iface_with_attach(self):
        network_id = None
        port_id = None
        iface_id = "flavor crystals"
        try:
            # Pre-populate data for testing using db api
            net = db.network_create(self.tenant_id, self.network_name_1)
            network_id = net['uuid']
            port = db.port_create(network_id)
            port_id = port['uuid']
            db.port_set_attachment(port_id, network_id, iface_id)
            cli.show_iface(self.client,
                           self.tenant_id,
                           network_id,
                           port_id,
                           self.version)
        except:
            LOG.exception("Exception caught: %s", sys.exc_info())
            self.fail("test_show_iface_with_attach failed due" +
                      " to an exception")

        LOG.debug("Operation completed. Verifying result")
        LOG.debug(self.fake_stdout.content)
        self._verify_show_iface(network_id, port_id)
