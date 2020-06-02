# Copyright 2016 Huawei Technologies India Pvt. Ltd.
# All Rights Reserved.
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

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.neutron.v2_0.bgp import speaker as bgp_speaker


def add_common_args(parser):
    parser.add_argument('dragent_id',
                        metavar='BGP_DRAGENT_ID',
                        help=_('ID of the Dynamic Routing agent.'))
    parser.add_argument('bgp_speaker',
                        metavar='BGP_SPEAKER',
                        help=_('ID or name of the BGP speaker.'))


class AddBGPSpeakerToDRAgent(neutronV20.NeutronCommand):
    """Add a BGP speaker to a Dynamic Routing agent."""

    def get_parser(self, prog_name):
        parser = super(AddBGPSpeakerToDRAgent, self).get_parser(prog_name)
        add_common_args(parser)
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _speaker_id = bgp_speaker.get_bgp_speaker_id(neutron_client,
                                                     parsed_args.bgp_speaker)
        neutron_client.add_bgp_speaker_to_dragent(
            parsed_args.dragent_id, {'bgp_speaker_id': _speaker_id})
        print(_('Associated BGP speaker %s to the Dynamic Routing agent.')
              % parsed_args.bgp_speaker, file=self.app.stdout)


class RemoveBGPSpeakerFromDRAgent(neutronV20.NeutronCommand):
    """Removes a BGP speaker from a Dynamic Routing agent."""

    def get_parser(self, prog_name):
        parser = super(RemoveBGPSpeakerFromDRAgent, self).get_parser(
            prog_name)
        add_common_args(parser)
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _speaker_id = bgp_speaker.get_bgp_speaker_id(neutron_client,
                                                     parsed_args.bgp_speaker)
        neutron_client.remove_bgp_speaker_from_dragent(parsed_args.dragent_id,
                                                       _speaker_id)
        print(_('Disassociated BGP speaker %s from the '
                'Dynamic Routing agent.')
              % parsed_args.bgp_speaker, file=self.app.stdout)


class ListBGPSpeakersOnDRAgent(neutronV20.ListCommand):
    """List BGP speakers hosted by a Dynamic Routing agent."""

    list_columns = ['id', 'name', 'local_as', 'ip_version']
    resource = 'bgp_speaker'

    def get_parser(self, prog_name):
        parser = super(ListBGPSpeakersOnDRAgent,
                       self).get_parser(prog_name)
        parser.add_argument(
            'dragent_id',
            metavar='BGP_DRAGENT_ID',
            help=_('ID of the Dynamic Routing agent.'))
        return parser

    def call_server(self, neutron_client, search_opts, parsed_args):
        data = neutron_client.list_bgp_speaker_on_dragent(
            parsed_args.dragent_id, **search_opts)
        return data


class ListDRAgentsHostingBGPSpeaker(neutronV20.ListCommand):
    """List Dynamic Routing agents hosting a BGP speaker."""

    resource = 'agent'
    _formatters = {}
    list_columns = ['id', 'host', 'admin_state_up', 'alive']
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListDRAgentsHostingBGPSpeaker,
                       self).get_parser(prog_name)
        parser.add_argument('bgp_speaker',
                            metavar='BGP_SPEAKER',
                            help=_('ID or name of the BGP speaker.'))
        return parser

    def extend_list(self, data, parsed_args):
        for agent in data:
            agent['alive'] = ":-)" if agent['alive'] else 'xxx'

    def call_server(self, neutron_client, search_opts, parsed_args):
        _speaker_id = bgp_speaker.get_bgp_speaker_id(neutron_client,
                                                     parsed_args.bgp_speaker)
        search_opts['bgp_speaker'] = _speaker_id
        data = neutron_client.list_dragents_hosting_bgp_speaker(**search_opts)
        return data
