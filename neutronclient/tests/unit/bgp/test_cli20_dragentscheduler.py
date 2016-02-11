# Copyright 2016 Huawei Technologies India Pvt. Ltd.
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

from neutronclient.neutron.v2_0.bgp import dragentscheduler as bgp_drsched
from neutronclient.tests.unit import test_cli20
from neutronclient.tests.unit import test_cli20_agentschedulers as test_as


BGP_DRAGENT_ID = 'bgp_dragent_id1'
BGP_SPEAKER = 'bgp_speaker_id1'


class CLITestV20DRAgentScheduler(test_as.CLITestV20AgentScheduler):

    def test_add_bgp_speaker_to_dragent(self):
        resource = 'agent'
        cmd = bgp_drsched.AddBGPSpeakerToDRAgent(
            test_cli20.MyApp(sys.stdout), None)
        args = (BGP_DRAGENT_ID, BGP_SPEAKER)
        body = {'bgp_speaker_id': BGP_SPEAKER}
        result = {'bgp_speaker_id': 'bgp_speaker_id', }
        self._test_add_to_agent(resource, cmd, args,
                                self.client.BGP_DRINSTANCES,
                                body, result)

    def test_remove_bgp_speaker_from_dragent(self):
        resource = 'agent'
        cmd = bgp_drsched.RemoveBGPSpeakerFromDRAgent(
            test_cli20.MyApp(sys.stdout), None)
        args = (BGP_DRAGENT_ID, BGP_SPEAKER)
        self._test_remove_from_agent(resource, cmd, args,
                                     self.client.BGP_DRINSTANCES)

    def test_list_bgp_speakers_on_dragent(self):
        resources = 'bgp_speakers'
        cmd = bgp_drsched.ListBGPSpeakersOnDRAgent(
            test_cli20.MyApp(sys.stdout), None)
        path = ((self.client.agent_path + self.client.BGP_DRINSTANCES) %
                BGP_DRAGENT_ID)
        self._test_list_resources(resources, cmd, base_args=[BGP_DRAGENT_ID],
                                  path=path)

    def test_list_dragents_hosting_bgp_speaker(self):
        resources = 'agent'
        cmd = bgp_drsched.ListDRAgentsHostingBGPSpeaker(
            test_cli20.MyApp(sys.stdout), None)
        path = ((self.client.bgp_speaker_path + self.client.BGP_DRAGENTS) %
                BGP_DRAGENT_ID)
        contents = {self.id_field: 'myid1', 'alive': True}
        self._test_list_resources(resources, cmd, base_args=[BGP_DRAGENT_ID],
                                  path=path, response_contents=contents)
