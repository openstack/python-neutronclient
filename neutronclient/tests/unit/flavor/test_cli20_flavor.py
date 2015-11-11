# Copyright 2015 Hewlett-Packard Development Company, L.P.
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

from neutronclient.neutron.v2_0.flavor import flavor
from neutronclient.tests.unit import test_cli20


class CLITestV20FlavorJSON(test_cli20.CLITestV20Base):

    def setUp(self):
        """Prepare test environment."""
        super(CLITestV20FlavorJSON, self).setUp(plurals={'flavors': 'flavor'})
        self.register_non_admin_status_resource('flavor')
        self.register_non_admin_status_resource('service_profile')

    def test_create_flavor_with_missing_params(self):
        """Create test flavor with missing parameters."""
        resource = 'flavor'
        cmd = flavor.CreateFlavor(
            test_cli20.MyApp(sys.stdout), None)
        name = 'Test flavor'
        myid = 'myid'
        position_names = []
        position_values = []
        args = []
        self.assertRaises(
            SystemExit, self._test_create_resource,
            resource, cmd, name, myid, args, position_names, position_values)

    def test_create_flavor_with_mandatory_params(self):
        """Create test flavor with minimal parameters."""
        resource = 'flavor'
        cmd = flavor.CreateFlavor(
            test_cli20.MyApp(sys.stdout), None)
        name = 'Test flavor'
        myid = 'myid'
        service_type = 'DUMMY'
        # Defaults are returned in body
        position_names = ['name', 'service_type']
        position_values = [name, service_type]
        args = [name, service_type]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_flavor_with_optional_params(self):
        """Create test flavor including optional parameters."""
        resource = 'flavor'
        cmd = flavor.CreateFlavor(
            test_cli20.MyApp(sys.stdout), None)
        name = 'Test flavor'
        myid = 'myid'
        service_type = 'DUMMY'
        description = 'Test description'
        position_names = ['name', 'service_type', 'description', 'enabled']
        position_values = [name, service_type, description, 'False']
        args = [name, service_type,
                '--description', description,
                '--enabled=False']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_delete_flavor(self):
        """Delete flavor."""
        resource = 'flavor'
        cmd = flavor.DeleteFlavor(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_list_flavors(self):
        """List flavors test."""
        resources = 'flavors'
        cmd = flavor.ListFlavor(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_flavors_with_pagination(self):
        """List flavors test with pagination."""
        resources = 'flavors'
        cmd = flavor.ListFlavor(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_flavors_with_sort(self):
        """List flavors test with sorting by name and id."""
        resources = 'flavors'
        cmd = flavor.ListFlavor(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_show_flavor(self):
        """Show flavor test."""
        resource = 'flavor'
        cmd = flavor.ShowFlavor(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'])

    def test_update_flavor_with_name(self):
        """Update flavor test."""
        resource = 'flavor'
        cmd = flavor.UpdateFlavor(
            test_cli20.MyApp(sys.stdout), None)
        newname = 'Test New Name'
        newdescription = 'New Description'
        args = ['--name', newname,
                '--description', newdescription,
                '--enabled', 'False', self.test_id]
        self._test_update_resource(resource, cmd, self.test_id, args,
                                   {'name': newname,
                                    'description': newdescription,
                                    'enabled': 'False'})

    def test_associate_flavor(self):
        """Associate flavor test."""
        resource = 'service_profile'
        cmd = flavor.AssociateFlavor(test_cli20.MyApp(sys.stdout), None)
        flavor_id = 'flavor-id'
        profile_id = 'profile-id'
        name = ''
        args = [flavor_id, profile_id]
        position_names = ['id']
        position_values = [profile_id]
        self._test_create_resource(resource, cmd, name, profile_id, args,
                                   position_names, position_values,
                                   cmd_resource='flavor_profile_binding',
                                   parent_id=flavor_id)

    def test_disassociate_flavor(self):
        """Disassociate flavor test."""
        resource = 'flavor_profile_binding'
        cmd = flavor.DisassociateFlavor(test_cli20.MyApp(sys.stdout), None)
        flavor_id = 'flavor-id'
        profile_id = 'profile-id'
        args = [flavor_id, profile_id]
        self._test_delete_resource(resource, cmd, profile_id, args,
                                   parent_id=flavor_id)
