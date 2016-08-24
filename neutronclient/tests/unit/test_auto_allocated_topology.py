# Copyright 2016 IBM
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

import sys

from neutronclient.neutron.v2_0 import auto_allocated_topology as aat
from neutronclient.tests.unit import test_cli20


class TestAutoAllocatedTopologyJSON(test_cli20.CLITestV20Base):

    def test_show_auto_allocated_topology_arg(self):
        resource = 'auto_allocated_topology'
        cmd = aat.ShowAutoAllocatedTopology(test_cli20.MyApp(sys.stdout), None)
        args = ['--tenant-id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args)

    def test_show_auto_allocated_topology_posarg(self):
        resource = 'auto_allocated_topology'
        cmd = aat.ShowAutoAllocatedTopology(test_cli20.MyApp(sys.stdout), None)
        args = ['some-tenant']
        self._test_show_resource(resource, cmd, "some-tenant", args)

    def test_show_auto_allocated_topology_no_arg(self):
        resource = 'auto_allocated_topology'
        cmd = aat.ShowAutoAllocatedTopology(test_cli20.MyApp(sys.stdout), None)
        args = []
        self._test_show_resource(resource, cmd, "None", args)

    def test_show_auto_allocated_topology_dry_run_as_tenant(self):
        resource = 'auto_allocated_topology'
        cmd = aat.ShowAutoAllocatedTopology(test_cli20.MyApp(sys.stdout), None)
        args = ['--dry-run']
        self._test_show_resource(resource, cmd, "None", args,
                                 fields=('dry-run',))

    def test_show_auto_allocated_topology_dry_run_as_admin(self):
        resource = 'auto_allocated_topology'
        cmd = aat.ShowAutoAllocatedTopology(test_cli20.MyApp(sys.stdout), None)
        args = ['--dry-run', 'some-tenant']
        self._test_show_resource(resource, cmd, "some-tenant", args,
                                 fields=('dry-run',))

    def test_delete_auto_allocated_topology_arg(self):
        resource = 'auto_allocated_topology'
        cmd = aat.DeleteAutoAllocatedTopology(test_cli20.MyApp(sys.stdout),
                                              None)
        args = ['--tenant-id', self.test_id]
        self._test_delete_resource(resource, cmd, self.test_id, args)

    def test_delete_auto_allocated_topology_posarg(self):
        resource = 'auto_allocated_topology'
        cmd = aat.DeleteAutoAllocatedTopology(test_cli20.MyApp(sys.stdout),
                                              None)
        args = ['some-tenant']
        self._test_delete_resource(resource, cmd, "some-tenant", args)

    def test_delete_auto_allocated_topology_no_arg(self):
        resource = 'auto_allocated_topology'
        cmd = aat.DeleteAutoAllocatedTopology(test_cli20.MyApp(sys.stdout),
                                              None)
        args = []
        self._test_delete_resource(resource, cmd, "None", args)
