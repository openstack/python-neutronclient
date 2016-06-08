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

from neutronclient.neutron.v2_0.qos import bandwidth_limit_rule as bw_rule
from neutronclient.tests.unit import test_cli20


class CLITestV20QoSBandwidthLimitRuleJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['bandwidth_limit_rule']

    def setUp(self):
        super(CLITestV20QoSBandwidthLimitRuleJSON, self).setUp()
        self.res = 'bandwidth_limit_rule'
        self.cmd_res = 'qos_bandwidth_limit_rule'
        self.ress = self.res + 's'
        self.cmd_ress = self.cmd_res + 's'

    def test_create_bandwidth_limit_rule_with_max_kbps(self):
        cmd = bw_rule.CreateQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        max_kbps = '1337'
        policy_id = 'policy_id'
        args = ['--max-kbps', max_kbps, policy_id]
        position_names = ['max_kbps']
        position_values = [max_kbps]
        self._test_create_resource(self.res, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_create_bandwidth_limit_rule_with_max_burst_kbps(self):
        cmd = bw_rule.CreateQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        max_burst_kbps = '1337'
        policy_id = 'policy_id'
        args = ['--max-burst-kbps', max_burst_kbps, policy_id]
        position_names = ['max_burst_kbps']
        position_values = [max_burst_kbps]
        self._test_create_resource(self.res, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_create_bandwidth_limit_rule_with_all_params(self):
        cmd = bw_rule.CreateQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        max_kbps = '1337'
        max_burst_kbps = '1337'
        policy_id = 'policy_id'
        args = ['--max-kbps', max_kbps,
                '--max-burst-kbps', max_burst_kbps,
                policy_id]
        position_names = ['max_kbps', 'max_burst_kbps']
        position_values = [max_kbps, max_burst_kbps]
        self._test_create_resource(self.res, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_update_bandwidth_limit_rule_with_max_kbps(self):
        cmd = bw_rule.UpdateQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        max_kbps = '1337'
        policy_id = 'policy_id'
        args = ['--max-kbps', max_kbps, my_id, policy_id]
        self._test_update_resource(self.res, cmd, my_id, args,
                                   {'max_kbps': max_kbps, },
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_update_bandwidth_limit_rule_with_max_burst_kbps(self):
        cmd = bw_rule.UpdateQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        max_burst_kbps = '1337'
        policy_id = 'policy_id'
        args = ['--max-burst-kbps', max_burst_kbps,
                my_id, policy_id]
        self._test_update_resource(self.res, cmd, my_id, args,
                                   {'max_burst_kbps': max_burst_kbps},
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_update_bandwidth_limit_rule_with_all_params(self):
        cmd = bw_rule.UpdateQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        max_kbps = '1337'
        max_burst_kbps = '1337'
        policy_id = 'policy_id'
        args = ['--max-kbps', max_kbps,
                '--max-burst-kbps', max_burst_kbps,
                my_id, policy_id]
        self._test_update_resource(self.res, cmd, my_id, args,
                                   {'max_kbps': max_kbps,
                                    'max_burst_kbps': max_burst_kbps},
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_delete_bandwidth_limit_rule(self):
        cmd = bw_rule.DeleteQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                  None)
        my_id = 'my-id'
        policy_id = 'policy_id'
        args = [my_id, policy_id]
        self._test_delete_resource(self.res, cmd, my_id, args,
                                   cmd_resource=self.cmd_res,
                                   parent_id=policy_id)

    def test_show_bandwidth_limit_rule(self):
        cmd = bw_rule.ShowQoSBandwidthLimitRule(test_cli20.MyApp(sys.stdout),
                                                None)
        policy_id = 'policy_id'
        args = ['--fields', 'id', self.test_id, policy_id]
        self._test_show_resource(self.res, cmd, self.test_id, args,
                                 ['id'], cmd_resource=self.cmd_res,
                                 parent_id=policy_id)
