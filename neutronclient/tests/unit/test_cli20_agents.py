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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from neutronclient.common import utils
from neutronclient.neutron.v2_0 import agent
from neutronclient.tests.unit import test_cli20


class CLITestV20Agent(test_cli20.CLITestV20Base):
    def test_list_agents(self):
        contents = {'agents': [{'id': 'myname', 'agent_type': 'mytype',
                                'alive': True}]}
        args = ['-f', 'json']
        resources = "agents"

        cmd = agent.ListAgent(test_cli20.MyApp(sys.stdout), None)
        self._test_list_columns(cmd, resources, contents, args)
        _str = self.fake_stdout.make_string()

        returned_agents = utils.loads(_str)
        self.assertEqual(1, len(returned_agents))
        ag = returned_agents[0]
        self.assertEqual(3, len(ag))
        self.assertIn("alive", ag.keys())

    def test_list_agents_field(self):
        contents = {'agents': [{'alive': True}]}
        args = ['-f', 'json']
        resources = "agents"
        smile = ':-)'

        cmd = agent.ListAgent(test_cli20.MyApp(sys.stdout), None)
        self._test_list_columns(cmd, resources, contents, args)
        _str = self.fake_stdout.make_string()

        returned_agents = utils.loads(_str)
        self.assertEqual(1, len(returned_agents))
        ag = returned_agents[0]
        self.assertEqual(1, len(ag))
        self.assertEqual("alive", ag.keys()[0])
        self.assertEqual(smile, ag.values()[0])
