# Copyright 2016 Comcast Inc.
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

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0.qos import dscp_marking_rule as dscp_rule
from neutronclient.tests.unit import test_cli20


class CLITestV20QoSDscpMarkingRuleJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['dscp_marking_rule']

    def setUp(self):
        super(CLITestV20QoSDscpMarkingRuleJSON, self).setUp()
        self.dscp_res = 'dscp_marking_rule'
        self.dscp_cmd_res = 'qos_dscp_marking_rule'
        self.dscp_ress = self.dscp_res + 's'
        self.dscp_cmd_ress = self.dscp_cmd_res + 's'

    def test_create_dscp_marking_rule_with_dscp_mark(self):
        cmd = dscp_rule.CreateQoSDscpMarkingRule(test_cli20.MyApp(sys.stdout),
                                                 None)
        my_id = 'my-id'
        policy_id = 'policy_id'
        position_names = ['dscp_mark']
        valid_dscp_marks = ['0', '56']
        invalid_dscp_marks = ['-1', '19', '42', '44', '57', '58']
        for dscp_mark in valid_dscp_marks:
            args = ['--dscp-mark', dscp_mark, policy_id]
            position_values = [dscp_mark]
            self._test_create_resource(self.dscp_res, cmd, '', my_id, args,
                                       position_names, position_values,
                                       cmd_resource=self.dscp_cmd_res,
                                       parent_id=policy_id)
        for dscp_mark in invalid_dscp_marks:
            args = ['--dscp-mark', dscp_mark, policy_id]
            position_values = [dscp_mark]
            self._test_create_resource(
                self.dscp_res, cmd, '', my_id, args,
                position_names, position_values,
                cmd_resource=self.dscp_cmd_res,
                parent_id=policy_id,
                no_api_call=True,
                expected_exception=exceptions.CommandError)

    def test_update_dscp_marking_rule_with_dscp_mark(self):
        cmd = dscp_rule.UpdateQoSDscpMarkingRule(test_cli20.MyApp(sys.stdout),
                                                 None)
        my_id = 'my-id'
        dscp_mark = '56'
        policy_id = 'policy_id'
        args = ['--dscp-mark', dscp_mark,
                my_id, policy_id]
        self._test_update_resource(self.dscp_res, cmd, my_id, args,
                                   {'dscp_mark': dscp_mark},
                                   cmd_resource=self.dscp_cmd_res,
                                   parent_id=policy_id)

    def test_delete_dscp_marking_rule(self):
        cmd = dscp_rule.DeleteQoSDscpMarkingRule(test_cli20.MyApp(sys.stdout),
                                                 None)
        my_id = 'my-id'
        policy_id = 'policy_id'
        args = [my_id, policy_id]
        self._test_delete_resource(self.dscp_res, cmd, my_id, args,
                                   cmd_resource=self.dscp_cmd_res,
                                   parent_id=policy_id)

    def test_show_dscp_marking_rule(self):
        cmd = dscp_rule.ShowQoSDscpMarkingRule(test_cli20.MyApp(sys.stdout),
                                               None)
        policy_id = 'policy_id'
        args = ['--fields', 'id', self.test_id, policy_id]
        self._test_show_resource(self.dscp_res, cmd, self.test_id, args,
                                 ['id'], cmd_resource=self.dscp_cmd_res,
                                 parent_id=policy_id)
