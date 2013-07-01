# Copyright 2013 Mirantis Inc.
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
# @author: Oleg Bondarev, Mirantis Inc.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from neutronclient.neutron.v2_0 import agentscheduler
from neutronclient.tests.unit import test_cli20


class CLITestV20LBaaSAgentScheduler(test_cli20.CLITestV20Base):

    def test_list_pools_on_agent(self):
        resources = 'pools'
        cmd = agentscheduler.ListPoolsOnLbaasAgent(
            test_cli20.MyApp(sys.stdout), None)
        agent_id = 'agent_id1'
        path = ((self.client.agent_path + self.client.LOADBALANCER_POOLS) %
                agent_id)
        self._test_list_resources(resources, cmd, base_args=[agent_id],
                                  path=path)

    def test_get_lbaas_agent_hosting_pool(self):
        resources = 'agent'
        cmd = agentscheduler.GetLbaasAgentHostingPool(
            test_cli20.MyApp(sys.stdout), None)
        pool_id = 'pool_id1'
        path = ((self.client.pool_path + self.client.LOADBALANCER_AGENT) %
                pool_id)
        contents = {self.id_field: 'myid1', 'alive': True}
        self._test_list_resources(resources, cmd, base_args=[pool_id],
                                  path=path, response_contents=contents)


class CLITestV20LBaaSAgentSchedulerXML(CLITestV20LBaaSAgentScheduler):
    format = 'xml'
