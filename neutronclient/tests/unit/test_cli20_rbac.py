# Copyright 2015 Huawei Technologies India Pvt Ltd.
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

import sys

import testscenarios

from neutronclient.neutron.v2_0 import rbac
from neutronclient.tests.unit import test_cli20

load_tests = testscenarios.load_tests_apply_scenarios


class CLITestV20RBACBaseJSON(test_cli20.CLITestV20Base):
    non_admin_status_resources = ['rbac_policy']

    scenarios = [
        ('network rbac objects',
         {'object_type_name': 'network', 'object_type_val': 'network'}),
        ('qos policy rbac objects',
         {'object_type_name': 'qos-policy', 'object_type_val': 'qos_policy'}),
    ]

    def test_create_rbac_policy_with_mandatory_params(self):
        # Create rbac: rbac_object --type <object_type_name> --action
        # access_as_shared
        resource = 'rbac_policy'
        cmd = rbac.CreateRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        name = 'rbac_object'
        myid = 'myid'
        args = [name, '--type', self.object_type_name,
                '--action', 'access_as_shared']
        position_names = ['object_id', 'object_type',
                          'target_tenant', 'action']
        position_values = [name, self.object_type_val, '*',
                           'access_as_shared']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_rbac_policy_with_all_params(self):
        # Create rbac: rbac_object --type <object_type_name>
        # --target-tenant tenant_id --action access_as_external
        resource = 'rbac_policy'
        cmd = rbac.CreateRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        name = 'rbac_object'
        myid = 'myid'
        args = [name, '--type', self.object_type_name,
                '--target-tenant', 'tenant_id',
                '--action', 'access_as_external']
        position_names = ['object_id', 'object_type',
                          'target_tenant', 'action']
        position_values = [name, self.object_type_val, 'tenant_id',
                           'access_as_external']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_rbac_policy_with_unicode(self):
        # Create rbac policy u'\u7f51\u7edc'.
        resource = 'rbac_policy'
        cmd = rbac.CreateRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        name = u'\u7f51\u7edc'
        myid = 'myid'
        args = [name, '--type', self.object_type_name,
                '--target-tenant', 'tenant_id',
                '--action', 'access_as_external']
        position_names = ['object_id', 'object_type',
                          'target_tenant', 'action']
        position_values = [name, self.object_type_val, 'tenant_id',
                           'access_as_external']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_update_rbac_policy(self):
        # rbac-update <rbac-uuid> --target-tenant <other-tenant-uuid>.
        resource = 'rbac_policy'
        cmd = rbac.UpdateRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--target-tenant', 'tenant_id'],
                                   {'target_tenant': 'tenant_id', })

    def test_delete_rbac_policy(self):
        # rbac-delete my-id.
        resource = 'rbac_policy'
        cmd = rbac.DeleteRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        my_id = 'myid1'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_list_rbac_policies(self):
        # rbac-list.
        resources = "rbac_policies"
        cmd = rbac.ListRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_rbac_policies_pagination(self):
        # rbac-list with pagination.
        resources = "rbac_policies"
        cmd = rbac.ListRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_rbac_policies_sort(self):
        # sorted list:
        # rbac-list --sort-key name --sort-key id --sort-key asc
        # --sort-key desc
        resources = "rbac_policies"
        cmd = rbac.ListRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_rbac_policies_limit(self):
        # size (1000) limited list: rbac-list -P.
        resources = "rbac_policies"
        cmd = rbac.ListRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_show_rbac_policy(self):
        # rbac-show test_id.
        resource = 'rbac_policy'
        cmd = rbac.ShowRBACPolicy(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'])
