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

from neutronclient.neutron.v2_0.qos import rule as qos_rule
from neutronclient.tests.unit import test_cli20


class CLITestV20QoSRuleJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['bandwidth_limit_rule',
                                  'dscp_marking_rule',
                                  'minimum_bandwidth_rule']

    def setUp(self):
        super(CLITestV20QoSRuleJSON, self).setUp()

    def test_list_qos_rule_types(self):
        # qos_rule_types.
        resources = 'rule_types'
        cmd_resources = 'qos_rule_types'
        response_contents = [{'type': 'bandwidth_limit',
                              'type': 'dscp_marking',
                              'type': 'minimum_bandwidth'}]

        cmd = qos_rule.ListQoSRuleTypes(test_cli20.MyApp(sys.stdout),
                                        None)
        self._test_list_resources(resources, cmd, True,
                                  response_contents=response_contents,
                                  cmd_resources=cmd_resources)
