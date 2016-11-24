# Copyright (c) 2016 Intel Corporation.
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

from neutronclient.neutron.v2_0.qos import minimum_bandwidth_rule as bw_rule
from neutronclient.tests.unit import test_cli20


class CLITestV20QoSMinimumBandwidthRuleJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['minimum_bandwidth_rule']

    def setUp(self):
        super(CLITestV20QoSMinimumBandwidthRuleJSON, self).setUp()
        self.res = 'minimum_bandwidth_rule'
        self.cmd_res = 'qos_minimum_bandwidth_rule'
        self.ress = self.res + 's'
        self.cmd_ress = self.cmd_res + 's'

    def test_create_minimum_bandwidth_rule_min_kbps_only(self):
        cmd = bw_rule.CreateQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        min_kbps = '1500'
        policy_id = 'policy_id'
        args = ['--min-kbps', min_kbps,
                policy_id]
        position_names = ['min_kbps']
        position_values = [min_kbps]
        self.assertRaises(SystemExit, self._test_create_resource,
                          self.res, cmd, '', my_id, args,
                          position_names, position_values,
                          cmd_resource=self.cmd_res,
                          parent_id=policy_id,
                          no_api_call=True)

    def test_create_minimum_bandwidth_rule_direction_only(self):
        cmd = bw_rule.CreateQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        direction = 'egress'
        policy_id = 'policy_id'
        args = ['--direction', direction,
                policy_id]
        position_names = ['direction']
        position_values = [direction]
        self.assertRaises(SystemExit, self._test_create_resource,
                          self.res, cmd, '', my_id, args,
                          position_names, position_values,
                          cmd_resource=self.cmd_res,
                          parent_id=policy_id,
                          no_api_call=True)

    def test_create_minimum_bandwidth_rule_none(self):
        cmd = bw_rule.CreateQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        policy_id = 'policy_id'
        args = [policy_id]
        position_names = []
        position_values = []
        self.assertRaises(SystemExit, self._test_create_resource,
                          self.res, cmd, '', my_id, args,
                          position_names, position_values,
                          cmd_resource=self.cmd_res,
                          parent_id=policy_id,
                          no_api_call=True)

    def test_create_minimum_bandwidth_rule_all(self):
        cmd = bw_rule.CreateQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        min_kbps = '1500'
        direction = 'egress'
        policy_id = 'policy_id'
        args = ['--min-kbps', min_kbps,
                '--direction', direction,
                policy_id]
        position_names = ['direction', 'min_kbps']
        position_values = [direction, min_kbps]
        self._test_create_resource(self.res, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_update_minimum_bandwidth_rule(self):
        cmd = bw_rule.UpdateQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        min_kbps = '1200'
        direction = 'egress'
        policy_id = 'policy_id'
        args = ['--min-kbps', min_kbps,
                '--direction', direction,
                my_id, policy_id]
        self._test_update_resource(self.res, cmd, my_id, args,
                                   {'min_kbps': min_kbps,
                                    'direction': direction},
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_delete_minimum_bandwidth_rule(self):
        cmd = bw_rule.DeleteQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        policy_id = 'policy_id'
        args = [my_id, policy_id]
        self._test_delete_resource(self.res, cmd, my_id, args,
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_show_minimum_bandwidth_rule(self):
        cmd = bw_rule.ShowQoSMinimumBandwidthRule(
            test_cli20.MyApp(sys.stdout), None)
        policy_id = 'policy_id'
        args = [self.test_id, policy_id]
        self._test_show_resource(self.res, cmd, self.test_id, args,
                                 [], cmd_resource=self.cmd_res,
                                 parent_id=policy_id)

    def test_list_minimum_bandwidth_rule(self):
        cmd = bw_rule.ListQoSMinimumBandwidthRules(
            test_cli20.MyApp(sys.stdout), None)
        policy_id = 'policy_id'
        args = [policy_id]
        contents = [{'name': 'rule1', 'min-kbps': 1000, 'direction': 'egress'}]
        self._test_list_resources(self.ress, cmd, parent_id=policy_id,
                                  cmd_resources=self.cmd_ress,
                                  base_args=args, response_contents=contents)
