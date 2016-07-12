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

from osc_lib.command import command
from osc_lib import utils

from neutronclient._i18n import _
from neutronclient.osc.v2.dynamic_routing import constants


def _format_alive_state(item):
    return ':-)' if item else 'XXX'


_formatters = {
    'alive': _format_alive_state
}


def add_common_args(parser):
    parser.add_argument('dragent_id',
                        metavar='<agent-id>',
                        help=_("ID of the dynamic routing agent"))
    parser.add_argument('bgp_speaker',
                        metavar='<bgp-speaker>',
                        help=_("ID or name of the BGP speaker"))


class AddBgpSpeakerToDRAgent(command.Command):
    """Add a BGP speaker to a dynamic routing agent"""

    def get_parser(self, prog_name):
        parser = super(AddBgpSpeakerToDRAgent, self).get_parser(prog_name)
        add_common_args(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        speaker_id = client.find_resource(constants.BGP_SPEAKER,
                                          parsed_args.bgp_speaker)['id']
        client.add_bgp_speaker_to_dragent(
            parsed_args.dragent_id, {'bgp_speaker_id': speaker_id})


class RemoveBgpSpeakerFromDRAgent(command.Command):
    """Removes a BGP speaker from a dynamic routing agent"""

    def get_parser(self, prog_name):
        parser = super(RemoveBgpSpeakerFromDRAgent, self).get_parser(
            prog_name)
        add_common_args(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        speaker_id = client.find_resource(constants.BGP_SPEAKER,
                                          parsed_args.bgp_speaker)['id']
        client.remove_bgp_speaker_from_dragent(parsed_args.dragent_id,
                                               speaker_id)


class ListDRAgentsHostingBgpSpeaker(command.Lister):
    """List dynamic routing agents hosting a BGP speaker"""

    resource = 'agent'
    list_columns = ['id', 'host', 'admin_state_up', 'alive']
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListDRAgentsHostingBgpSpeaker,
                       self).get_parser(prog_name)
        parser.add_argument('bgp_speaker',
                            metavar='<bgp-speaker>',
                            help=_("ID or name of the BGP speaker"))
        return parser

    def take_action(self, parsed_args):
        search_opts = {}
        client = self.app.client_manager.neutronclient
        speaker_id = client.find_resource(constants.BGP_SPEAKER,
                                          parsed_args.bgp_speaker)['id']
        search_opts['bgp_speaker'] = speaker_id
        data = client.list_dragents_hosting_bgp_speaker(**search_opts)
        headers = ('ID', 'Host', 'State', 'Alive')
        columns = ('id', 'host', 'admin_state_up', 'alive')
        return (headers,
                (utils.get_dict_properties(
                    s, columns, formatters=_formatters,
                ) for s in data['agents']))
