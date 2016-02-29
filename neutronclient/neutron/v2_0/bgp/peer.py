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
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.common import validators
from neutronclient.neutron import v2_0 as neutronv20


def get_bgp_peer_id(client, id_or_name):
    return neutronv20.find_resourceid_by_name_or_id(client,
                                                    'bgp_peer',
                                                    id_or_name)


def validate_peer_attributes(parsed_args):
    # Validate AS number
    validators.validate_int_range(parsed_args, 'remote_as',
                                  neutronv20.bgp.speaker.MIN_AS_NUM,
                                  neutronv20.bgp.speaker.MAX_AS_NUM)
    # Validate password
    if parsed_args.auth_type != 'none' and parsed_args.password is None:
        raise exceptions.CommandError(_('Must provide password if auth-type '
                                        'is specified.'))
    if parsed_args.auth_type == 'none' and parsed_args.password:
        raise exceptions.CommandError(_('Must provide auth-type if password '
                                        'is specified.'))


class ListPeers(neutronv20.ListCommand):
    """List BGP peers."""

    resource = 'bgp_peer'
    list_columns = ['id', 'name', 'peer_ip', 'remote_as']
    pagination_support = True
    sorting_support = True


class ShowPeer(neutronv20.ShowCommand):
    """Show information of a given BGP peer."""

    resource = 'bgp_peer'


class CreatePeer(neutronv20.CreateCommand):
    """Create a BGP Peer."""

    resource = 'bgp_peer'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='NAME',
            help=_('Name of the BGP peer to create.'))
        parser.add_argument(
            '--peer-ip',
            metavar='PEER_IP_ADDRESS',
            required=True,
            help=_('Peer IP address.'))
        parser.add_argument(
            '--remote-as',
            required=True,
            metavar='PEER_REMOTE_AS',
            help=_('Peer AS number. (Integer in [%(min_val)s, %(max_val)s] '
                   'is allowed.)') %
            {'min_val': neutronv20.bgp.speaker.MIN_AS_NUM,
             'max_val': neutronv20.bgp.speaker.MAX_AS_NUM})
        parser.add_argument(
            '--auth-type',
            metavar='PEER_AUTH_TYPE',
            choices=['none', 'md5'],
            default='none',
            type=utils.convert_to_lowercase,
            help=_('Authentication algorithm. Supported algorithms: '
                   'none(default), md5'))
        parser.add_argument(
            '--password',
            metavar='AUTH_PASSWORD',
            help=_('Authentication password.'))

    def args2body(self, parsed_args):
        body = {}
        validate_peer_attributes(parsed_args)
        neutronv20.update_dict(parsed_args, body,
                               ['name', 'peer_ip',
                                'remote_as', 'auth_type', 'password'])
        return {self.resource: body}


class UpdatePeer(neutronv20.UpdateCommand):
    """Update BGP Peer's information."""

    resource = 'bgp_peer'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Updated name of the BGP peer.'))
        parser.add_argument(
            '--password',
            metavar='AUTH_PASSWORD',
            help=_('Updated authentication password.'))

    def args2body(self, parsed_args):
        body = {}
        neutronv20.update_dict(parsed_args, body, ['name', 'password'])
        return {self.resource: body}


class DeletePeer(neutronv20.DeleteCommand):
    """Delete a BGP peer."""

    resource = 'bgp_peer'
