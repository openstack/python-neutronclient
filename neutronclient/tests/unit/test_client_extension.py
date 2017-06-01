# Copyright 2015 Rackspace Hosting Inc.
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

import inspect
import sys

import mock

from neutronclient.common import extension
from neutronclient.neutron.v2_0.contrib import _fox_sockets as fox_sockets
from neutronclient import shell
from neutronclient.tests.unit import test_cli20


class CLITestV20ExtensionJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['fox_socket']

    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionJSON, self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        contrib.return_value = [("_fox_sockets", fox_sockets)]
        return contrib

    def test_ext_cmd_loaded(self):
        neutron_shell = shell.NeutronShell('2.0')
        ext_cmd = {'fox-sockets-list': fox_sockets.FoxInSocketsList,
                   'fox-sockets-create': fox_sockets.FoxInSocketsCreate,
                   'fox-sockets-update': fox_sockets.FoxInSocketsUpdate,
                   'fox-sockets-delete': fox_sockets.FoxInSocketsDelete,
                   'fox-sockets-show': fox_sockets.FoxInSocketsShow}
        for cmd_name, cmd_class in ext_cmd.items():
            found = neutron_shell.command_manager.find_command([cmd_name])
            self.assertEqual(cmd_class, found[0])

    def test_ext_cmd_help_doc_with_extension_name(self):
        neutron_shell = shell.NeutronShell('2.0')
        ext_cmd = {'fox-sockets-list': fox_sockets.FoxInSocketsList,
                   'fox-sockets-create': fox_sockets.FoxInSocketsCreate,
                   'fox-sockets-update': fox_sockets.FoxInSocketsUpdate,
                   'fox-sockets-delete': fox_sockets.FoxInSocketsDelete,
                   'fox-sockets-show': fox_sockets.FoxInSocketsShow}
        for cmd_name, cmd_class in ext_cmd.items():
            found = neutron_shell.command_manager.find_command([cmd_name])
            found_factory = found[0]
            self.assertEqual(cmd_class, found_factory)
            self.assertTrue(found_factory.__doc__.startswith("[_fox_sockets]"))

    def test_delete_fox_socket(self):
        # Delete fox socket: myid.
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsDelete(test_cli20.MyApp(sys.stdout),
                                             None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_update_fox_socket(self):
        # Update fox_socket: myid --name myname.
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsUpdate(test_cli20.MyApp(sys.stdout),
                                             None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname'],
                                   {'name': 'myname'})

    def test_create_fox_socket(self):
        # Create fox_socket: myname.
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsCreate(test_cli20.MyApp(sys.stdout),
                                             None)
        name = 'myname'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_list_fox_sockets(self):
        # List fox_sockets.
        resources = 'fox_sockets'
        cmd = fox_sockets.FoxInSocketsList(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_fox_pagination(self):
        resources = 'fox_sockets'
        cmd = fox_sockets.FoxInSocketsList(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_show_fox_socket(self):
        # Show fox_socket: --fields id --fields name myid.
        resource = 'fox_socket'
        cmd = fox_sockets.FoxInSocketsShow(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])


class CLITestV20ExtensionJSONAlternatePlurals(test_cli20.CLITestV20Base):
    class IPAddress(extension.NeutronClientExtension):
        resource = 'ip_address'
        resource_plural = '%ses' % resource
        object_path = '/%s' % resource_plural
        resource_path = '/%s/%%s' % resource_plural
        versions = ['2.0']

    class IPAddressesList(extension.ClientExtensionList, IPAddress):
        shell_command = 'ip-address-list'

    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionJSONAlternatePlurals, self).setUp()

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        ip_address = mock.Mock()
        ip_address.IPAddress = self.IPAddress
        ip_address.IPAddressesList = self.IPAddressesList
        contrib.return_value = [("ip_address", ip_address)]
        return contrib

    def test_ext_cmd_loaded(self):
        neutron_shell = shell.NeutronShell('2.0')
        ext_cmd = {'ip-address-list': self.IPAddressesList}
        for cmd_name, cmd_class in ext_cmd.items():
            found = neutron_shell.command_manager.find_command([cmd_name])
            self.assertEqual(cmd_class, found[0])

    def test_list_ip_addresses(self):
        # List ip_addresses.
        resources = 'ip_addresses'
        cmd = self.IPAddressesList(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)


class CLITestV20ExtensionJSONChildResource(test_cli20.CLITestV20Base):
    class Child(extension.NeutronClientExtension):
        parent_resource = 'parents'
        child_resource = 'child'
        resource = '%s_%s' % (parent_resource, child_resource)
        resource_plural = '%sren' % resource
        child_resource_plural = '%ren' % child_resource
        object_path = '/%s/%%s/%s' % (parent_resource, child_resource_plural)
        resource_path = '/%s/%%s/%s/%%s' % (parent_resource,
                                            child_resource_plural)
        versions = ['2.0']

    class ChildrenList(extension.ClientExtensionList, Child):
        shell_command = 'parent-child-list'

    class ChildShow(extension.ClientExtensionShow, Child):
        shell_command = 'parent-child-show'

    class ChildUpdate(extension.ClientExtensionUpdate, Child):
        shell_command = 'parent-child-update'

    class ChildDelete(extension.ClientExtensionDelete, Child):
        shell_command = 'parent-child-delete'

    class ChildCreate(extension.ClientExtensionCreate, Child):
        shell_command = 'parent-child-create'

    def setUp(self):
        # need to mock before super because extensions loaded on instantiation
        self._mock_extension_loading()
        super(CLITestV20ExtensionJSONChildResource, self).setUp()

    def _mock_extension_loading(self):
        ext_pkg = 'neutronclient.common.extension'
        contrib = mock.patch(ext_pkg + '._discover_via_entry_points').start()
        child = mock.Mock()
        child.Child = self.Child
        child.ChildrenList = self.ChildrenList
        child.ChildShow = self.ChildShow
        child.ChildUpdate = self.ChildUpdate
        child.ChildDelete = self.ChildDelete
        child.ChildCreate = self.ChildCreate
        contrib.return_value = [("child", child)]
        return contrib

    def test_ext_cmd_loaded(self):
        neutron_shell = shell.NeutronShell('2.0')
        ext_cmd = {'parent-child-list': self.ChildrenList,
                   'parent-child-show': self.ChildShow,
                   'parent-child-update': self.ChildUpdate,
                   'parent-child-delete': self.ChildDelete,
                   'parent-child-create': self.ChildCreate}
        for cmd_name, cmd_class in ext_cmd.items():
            found = neutron_shell.command_manager.find_command([cmd_name])
            self.assertEqual(cmd_class, found[0])

    def test_client_methods_have_parent_id_arg(self):
        methods = (self.client.list_parents_children,
                   self.client.show_parents_child,
                   self.client.update_parents_child,
                   self.client.delete_parents_child,
                   self.client.create_parents_child)
        for method in methods:
            argspec = inspect.getargspec(method)
            self.assertIn("parent_id", argspec.args)
