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

from neutronclient.neutron.v2_0.flavor import flavor_profile
from neutronclient.tests.unit import test_cli20


class CLITestV20FlavorProfileJSON(test_cli20.CLITestV20Base):

    def setUp(self):
        """Prepare test environment."""
        super(CLITestV20FlavorProfileJSON, self).setUp(
            plurals={'service_profiles': 'service_profile'})
        self.register_non_admin_status_resource('service_profile')

    def test_create_flavor_profile_with_mandatory_params(self):
        """Create test flavor profile test."""
        resource = 'service_profile'
        cmd = flavor_profile.CreateFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        name = ''
        description = 'Test flavor profile'
        myid = 'myid'
        metainfo = "{'a':'b'}"
        # Defaults are returned in body
        position_names = ['description', 'metainfo']
        position_values = [description, metainfo]
        args = ['--description', description, '--metainfo', metainfo]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_flavor_profile_with_optional_params(self):
        """Create test flavor profile disabled test."""
        resource = 'service_profile'
        cmd = flavor_profile.CreateFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        name = ''
        description = 'Test flavor profile - disabled'
        myid = 'myid'
        driver = 'mydriver'
        metainfo = "{'a':'b'}"
        position_names = ['description', 'driver', 'metainfo', 'enabled']
        position_values = [description, driver, metainfo, 'False']
        args = ['--description', description, '--driver', driver,
                '--metainfo', metainfo, '--enabled=False']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_list_flavor_profiles(self):
        """List flavor profiles test."""
        resources = 'service_profiles'
        cmd = flavor_profile.ListFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_flavor_profiles_with_pagination(self):
        """List flavor profiles test with pagination."""
        resources = 'service_profiles'
        cmd = flavor_profile.ListFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_flavor_profiles_with_sort(self):
        """List flavor profiles test with sort by description."""
        resources = 'service_profiles'
        cmd = flavor_profile.ListFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["description"],
                                  sort_dir=["asc"])

    def test_show_flavor_profile(self):
        """Show flavor profile test."""
        resource = 'service_profile'
        cmd = flavor_profile.ShowFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'])

    def test_update_flavor_profile(self):
        """Update flavor profile test."""
        resource = 'service_profile'
        cmd = flavor_profile.UpdateFlavorProfile(
            test_cli20.MyApp(sys.stdout), None)
        newdescription = 'Test new description'
        newdriver = 'NewDriver'
        newmetainfo = "{'c':'d'}"
        newenabled = "False"
        args = ['--description', newdescription,
                '--driver', newdriver,
                '--metainfo', newmetainfo,
                '--enabled', newenabled,
                self.test_id]
        self._test_update_resource(resource, cmd, self.test_id, args,
                                   {'description': newdescription,
                                    'driver': newdriver,
                                    'metainfo': newmetainfo,
                                    'enabled': newenabled})

    def test_delete_flavor_profile(self):
        """Delete flavor profile."""
        resource = 'service_profile'
        cmd = flavor_profile.DeleteFlavorProfile(test_cli20.MyApp(sys.stdout),
                                                 None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)
