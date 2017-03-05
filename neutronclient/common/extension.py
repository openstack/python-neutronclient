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
from stevedore import extension

from neutronclient.neutron import v2_0 as neutronV20


def _discover_via_entry_points():
    emgr = extension.ExtensionManager('neutronclient.extension',
                                      invoke_on_load=False)
    return ((ext.name, ext.plugin) for ext in emgr)


class NeutronClientExtension(neutronV20.NeutronCommand):
    pagination_support = False
    _formatters = {}
    sorting_support = False


class ClientExtensionShow(NeutronClientExtension, neutronV20.ShowCommand):
    def take_action(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionShow, self).take_action(parsed_args)


class ClientExtensionList(NeutronClientExtension, neutronV20.ListCommand):
    def take_action(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionList, self).take_action(parsed_args)


class ClientExtensionDelete(NeutronClientExtension, neutronV20.DeleteCommand):
    def take_action(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionDelete, self).take_action(parsed_args)


class ClientExtensionCreate(NeutronClientExtension, neutronV20.CreateCommand):
    def take_action(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionCreate, self).take_action(parsed_args)


class ClientExtensionUpdate(NeutronClientExtension, neutronV20.UpdateCommand):
    def take_action(self, parsed_args):
        # NOTE(mdietz): Calls 'execute' to provide a consistent pattern
        #               for any implementers adding extensions with
        #               regard to any other extension verb.
        return self.execute(parsed_args)

    def execute(self, parsed_args):
        return super(ClientExtensionUpdate, self).take_action(parsed_args)
