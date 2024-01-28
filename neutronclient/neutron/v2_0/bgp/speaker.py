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
from neutronclient.common import utils
from neutronclient.common import validators
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.bgp import peer as bgp_peer

# Allowed BGP Autonomous number range
MIN_AS_NUM = 1
MAX_AS_NUM = 4294967295


def get_network_id(client, id_or_name):
    return neutronv20.find_resourceid_by_name_or_id(client,
                                                    'network',
                                                    id_or_name)


def get_bgp_speaker_id(client, id_or_name):
    return neutronv20.find_resourceid_by_name_or_id(client,
                                                    'bgp_speaker',
                                                    id_or_name)


def validate_speaker_attributes(parsed_args):
    # Validate AS number
    validators.validate_int_range(parsed_args, 'local_as',
                                  MIN_AS_NUM, MAX_AS_NUM)


def add_common_arguments(parser):
    utils.add_boolean_argument(
        parser, '--advertise-floating-ip-host-routes',
        help=_('Whether to enable or disable the advertisement '
               'of floating-ip host routes by the BGP speaker. '
               'By default floating ip host routes will be '
               'advertised by the BGP speaker.'))
    utils.add_boolean_argument(
        parser, '--advertise-tenant-networks',
        help=_('Whether to enable or disable the advertisement '
               'of tenant network routes by the BGP speaker. '
               'By default tenant network routes will be '
               'advertised by the BGP speaker.'))


def args2body_common_arguments(body, parsed_args):
    neutronv20.update_dict(parsed_args, body,
                           ['name',
                            'advertise_floating_ip_host_routes',
                            'advertise_tenant_networks'])


class ListSpeakers(neutronv20.ListCommand):
    """List BGP speakers."""

    resource = 'bgp_speaker'
    list_columns = ['id', 'name', 'local_as', 'ip_version']
    pagination_support = True
    sorting_support = True


class ShowSpeaker(neutronv20.ShowCommand):
    """Show information of a given BGP speaker."""

    resource = 'bgp_speaker'


class CreateSpeaker(neutronv20.CreateCommand):
    """Create a BGP Speaker."""

    resource = 'bgp_speaker'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='NAME',
            help=_('Name of the BGP speaker to create.'))
        parser.add_argument(
            '--local-as',
            metavar='LOCAL_AS',
            required=True,
            help=_('Local AS number. (Integer in [%(min_val)s, %(max_val)s] '
                   'is allowed.)') % {'min_val': MIN_AS_NUM,
                                      'max_val': MAX_AS_NUM})
        parser.add_argument(
            '--ip-version',
            type=int, choices=[4, 6],
            default=4,
            help=_('IP version for the BGP speaker (default is 4).'))
        add_common_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        validate_speaker_attributes(parsed_args)
        body['local_as'] = parsed_args.local_as
        body['ip_version'] = parsed_args.ip_version
        args2body_common_arguments(body, parsed_args)
        return {self.resource: body}


class UpdateSpeaker(neutronv20.UpdateCommand):
    """Update BGP Speaker's information."""

    resource = 'bgp_speaker'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Name of the BGP speaker to update.'))
        add_common_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        args2body_common_arguments(body, parsed_args)
        return {self.resource: body}


class DeleteSpeaker(neutronv20.DeleteCommand):
    """Delete a BGP speaker."""

    resource = 'bgp_speaker'


class AddPeerToSpeaker(neutronv20.NeutronCommand):
    """Add a peer to the BGP speaker."""

    def get_parser(self, prog_name):
        parser = super(AddPeerToSpeaker, self).get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='BGP_SPEAKER',
            help=_('ID or name of the BGP speaker.'))
        parser.add_argument(
            'bgp_peer',
            metavar='BGP_PEER',
            help=_('ID or name of the BGP peer to add.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _speaker_id = get_bgp_speaker_id(neutron_client,
                                         parsed_args.bgp_speaker)
        _peer_id = bgp_peer.get_bgp_peer_id(neutron_client,
                                            parsed_args.bgp_peer)
        neutron_client.add_peer_to_bgp_speaker(_speaker_id,
                                               {'bgp_peer_id': _peer_id})
        print(_('Added BGP peer %(peer)s to BGP speaker %(speaker)s.') %
              {'peer': parsed_args.bgp_peer,
               'speaker': parsed_args.bgp_speaker},
              file=self.app.stdout)


class RemovePeerFromSpeaker(neutronv20.NeutronCommand):
    """Remove a peer from the BGP speaker."""

    def get_parser(self, prog_name):
        parser = super(RemovePeerFromSpeaker, self).get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='BGP_SPEAKER',
            help=_('ID or name of the BGP speaker.'))
        parser.add_argument(
            'bgp_peer',
            metavar='BGP_PEER',
            help=_('ID or name of the BGP peer to remove.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _speaker_id = get_bgp_speaker_id(neutron_client,
                                         parsed_args.bgp_speaker)
        _peer_id = bgp_peer.get_bgp_peer_id(neutron_client,
                                            parsed_args.bgp_peer)
        neutron_client.remove_peer_from_bgp_speaker(_speaker_id,
                                                    {'bgp_peer_id': _peer_id})
        print(_('Removed BGP peer %(peer)s from BGP speaker %(speaker)s.') %
              {'peer': parsed_args.bgp_peer,
               'speaker': parsed_args.bgp_speaker},
              file=self.app.stdout)


class AddNetworkToSpeaker(neutronv20.NeutronCommand):
    """Add a network to the BGP speaker."""

    def get_parser(self, prog_name):
        parser = super(AddNetworkToSpeaker, self).get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='BGP_SPEAKER',
            help=_('ID or name of the BGP speaker.'))
        parser.add_argument(
            'network',
            metavar='NETWORK',
            help=_('ID or name of the network to add.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _speaker_id = get_bgp_speaker_id(neutron_client,
                                         parsed_args.bgp_speaker)
        _net_id = get_network_id(neutron_client,
                                 parsed_args.network)
        neutron_client.add_network_to_bgp_speaker(_speaker_id,
                                                  {'network_id': _net_id})
        print(_('Added network %(net)s to BGP speaker %(speaker)s.') %
              {'net': parsed_args.network, 'speaker': parsed_args.bgp_speaker},
              file=self.app.stdout)


class RemoveNetworkFromSpeaker(neutronv20.NeutronCommand):
    """Remove a network from the BGP speaker."""

    def get_parser(self, prog_name):
        parser = super(RemoveNetworkFromSpeaker, self).get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='BGP_SPEAKER',
            help=_('ID or name of the BGP speaker.'))
        parser.add_argument(
            'network',
            metavar='NETWORK',
            help=_('ID or name of the network to remove.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        _speaker_id = get_bgp_speaker_id(neutron_client,
                                         parsed_args.bgp_speaker)
        _net_id = get_network_id(neutron_client,
                                 parsed_args.network)
        neutron_client.remove_network_from_bgp_speaker(_speaker_id,
                                                       {'network_id': _net_id})
        print(_('Removed network %(net)s from BGP speaker %(speaker)s.') %
              {'net': parsed_args.network, 'speaker': parsed_args.bgp_speaker},
              file=self.app.stdout)


class ListRoutesAdvertisedBySpeaker(neutronv20.ListCommand):
    """List routes advertised by a given BGP speaker."""

    list_columns = ['id', 'destination', 'next_hop']
    resource = 'advertised_route'
    pagination_support = True
    sorting_support = True

    def get_parser(self, prog_name):
        parser = super(ListRoutesAdvertisedBySpeaker,
                       self).get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='BGP_SPEAKER',
            help=_('ID or name of the BGP speaker.'))
        return parser

    def call_server(self, neutron_client, search_opts, parsed_args):
        _speaker_id = get_bgp_speaker_id(neutron_client,
                                         parsed_args.bgp_speaker)
        data = neutron_client.list_route_advertised_from_bgp_speaker(
            _speaker_id, **search_opts)
        return data
