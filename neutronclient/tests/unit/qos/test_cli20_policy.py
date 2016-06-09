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
#

import sys

from neutronclient.neutron.v2_0.qos import policy as policy
from neutronclient.tests.unit import test_cli20


class CLITestV20QoSPolicyJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['policy']

    def setUp(self):
        super(CLITestV20QoSPolicyJSON, self).setUp()
        self.res = 'policy'
        self.cmd_res = 'qos_policy'
        self.ress = "policies"
        self.cmd_ress = 'qos_policies'

    def test_create_policy_with_only_keyattributes(self):
        # Create qos policy abc.
        cmd = policy.CreateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        myid = 'myid'
        name = 'abc'
        args = [name]
        position_names = ['name']
        position_values = [name]
        self._test_create_resource(self.res, cmd, name, myid, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res)

    def test_create_policy_with_description(self):
        # Create qos policy xyz --description abc.
        cmd = policy.CreateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        myid = 'myid'
        name = 'abc'
        description = 'policy_abc'
        args = [name, '--description', description]
        position_names = ['name', 'description']
        position_values = [name, description]
        self._test_create_resource(self.res, cmd, name, myid, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res)

    def test_create_policy_with_shared(self):
        # Create qos policy abc shared across tenants
        cmd = policy.CreateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        myid = 'myid'
        name = 'abc'
        description = 'policy_abc'
        args = [name, '--description', description, '--shared']
        position_names = ['name', 'description', 'shared']
        position_values = [name, description, True]
        self._test_create_resource(self.res, cmd, name, myid, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res)

    def test_create_policy_with_unicode(self):
        # Create qos policy u'\u7f51\u7edc'.
        cmd = policy.CreateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        myid = 'myid'
        name = u'\u7f51\u7edc'
        description = u'\u7f51\u7edc'
        args = [name, '--description', description]
        position_names = ['name', 'description']
        position_values = [name, description]
        self._test_create_resource(self.res, cmd, name, myid, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res)

    def test_update_policy(self):
        # policy-update myid --name newname.
        cmd = policy.UpdateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        self._test_update_resource(self.res, cmd, 'myid',
                                   ['myid', '--name', 'newname'],
                                   {'name': 'newname', },
                                   cmd_resource=self.cmd_res)

    def test_update_policy_description(self):
        # policy-update myid --name newname --description newdesc
        cmd = policy.UpdateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        self._test_update_resource(self.res, cmd, 'myid',
                                   ['myid', '--description', 'newdesc'],
                                   {'description': 'newdesc', },
                                   cmd_resource=self.cmd_res)

    def test_update_policy_to_shared(self):
        # policy-update myid --shared
        cmd = policy.UpdateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        self._test_update_resource(self.res, cmd, 'myid',
                                   ['myid', '--shared'],
                                   {'shared': True, },
                                   cmd_resource=self.cmd_res)

    def test_update_policy_to_no_shared(self):
        # policy-update myid --no-shared
        cmd = policy.UpdateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        self._test_update_resource(self.res, cmd, 'myid',
                                   ['myid', '--no-shared'],
                                   {'shared': False, },
                                   cmd_resource=self.cmd_res)

    def test_update_policy_to_shared_no_shared_together(self):
        # policy-update myid --shared --no-shared
        cmd = policy.UpdateQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        self.assertRaises(
            SystemExit,
            self._test_update_resource,
            self.res, cmd, 'myid',
            ['myid', '--shared', '--no-shared'], {},
            cmd_resource=self.cmd_res
        )

    def test_list_policies(self):
        # qos-policy-list.
        cmd = policy.ListQoSPolicy(test_cli20.MyApp(sys.stdout),
                                   None)
        self._test_list_resources(self.ress, cmd, True,
                                  cmd_resources=self.cmd_ress)

    def test_list_policies_pagination(self):
        # qos-policy-list for pagination.
        cmd = policy.ListQoSPolicy(test_cli20.MyApp(sys.stdout),
                                   None)
        self._test_list_resources_with_pagination(self.ress, cmd,
                                                  cmd_resources=self.cmd_ress)

    def test_list_policies_sort(self):
        # sorted list: qos-policy-list --sort-key name --sort-key id
        # --sort-key asc --sort-key desc
        cmd = policy.ListQoSPolicy(test_cli20.MyApp(sys.stdout),
                                   None)
        self._test_list_resources(self.ress, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"],
                                  cmd_resources=self.cmd_ress)

    def test_list_policies_limit(self):
        # size (1000) limited list: qos-policy-list -P.
        cmd = policy.ListQoSPolicy(test_cli20.MyApp(sys.stdout),
                                   None)
        self._test_list_resources(self.ress, cmd, page_size=1000,
                                  cmd_resources=self.cmd_ress)

    def test_show_policy_id(self):
        # qos-policy-show test_id.
        cmd = policy.ShowQoSPolicy(test_cli20.MyApp(sys.stdout),
                                   None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(self.res, cmd, self.test_id, args,
                                 ['id'], cmd_resource=self.cmd_res)

    def test_show_policy_name(self):
        # qos-policy-show.
        cmd = policy.ShowQoSPolicy(test_cli20.MyApp(sys.stdout),
                                   None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(self.res, cmd, self.test_id,
                                 args, ['id', 'name'],
                                 cmd_resource=self.cmd_res)

    def test_delete_policy(self):
        # qos-policy-delete my-id.
        cmd = policy.DeleteQoSPolicy(test_cli20.MyApp(sys.stdout),
                                     None)
        my_id = 'myid1'
        args = [my_id]
        self._test_delete_resource(self.res, cmd, my_id, args,
                                   cmd_resource=self.cmd_res)
