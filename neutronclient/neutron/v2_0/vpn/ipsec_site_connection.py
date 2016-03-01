#    (c) Copyright 2013 Hewlett-Packard Development Company, L.P.
#    All Rights Reserved.
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

import argparse

from oslo_serialization import jsonutils

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.vpn import utils as vpn_utils


def _format_peer_cidrs(ipsec_site_connection):
    try:
        return '\n'.join([jsonutils.dumps(cidrs) for cidrs in
                          ipsec_site_connection['peer_cidrs']])
    except (TypeError, KeyError):
        return ''


class ListIPsecSiteConnection(neutronv20.ListCommand):
    """List IPsec site connections that belong to a given tenant."""

    resource = 'ipsec_site_connection'
    _formatters = {'peer_cidrs': _format_peer_cidrs}
    list_columns = [
        'id', 'name', 'peer_address', 'auth_mode', 'status']
    pagination_support = True
    sorting_support = True


class ShowIPsecSiteConnection(neutronv20.ShowCommand):
    """Show information of a given IPsec site connection."""

    resource = 'ipsec_site_connection'
    help_resource = 'IPsec site connection'


class IPsecSiteConnectionMixin(object):

    def add_known_arguments(self, parser, is_create=True):
        parser.add_argument(
            '--name',
            help=_('Set friendly name for the connection.'))
        parser.add_argument(
            '--description',
            help=_('Set a description for the connection.'))
        parser.add_argument(
            '--dpd',
            metavar="action=ACTION,interval=INTERVAL,timeout=TIMEOUT",
            type=utils.str2dict_type(
                optional_keys=['action', 'interval', 'timeout']),
            help=vpn_utils.dpd_help("IPsec connection."))
        parser.add_argument(
            '--local-ep-group',
            help=_('Local endpoint group ID/name with subnet(s) for '
                   'IPSec connection.'))
        parser.add_argument(
            '--peer-ep-group',
            help=_('Peer endpoint group ID/name with CIDR(s) for '
                   'IPSec connection.'))
        parser.add_argument(
            '--peer-cidr',
            action='append', dest='peer_cidrs',
            help=_('[DEPRECATED in Mitaka] Remote subnet(s) in CIDR format. '
                   'Cannot be specified when using endpoint groups. Only '
                   'applicable, if subnet provided for VPN service.'))
        parser.add_argument(
            '--peer-id',
            required=is_create,
            help=_('Peer router identity for authentication. Can be '
                   'IPv4/IPv6 address, e-mail address, key id, or FQDN.'))
        parser.add_argument(
            '--peer-address',
            required=is_create,
            help=_('Peer gateway public IPv4/IPv6 address or FQDN.'))
        parser.add_argument(
            '--psk',
            required=is_create,
            help=_('Pre-shared key string.'))
        parser.add_argument(
            '--mtu',
            default='1500' if is_create else argparse.SUPPRESS,
            help=_('MTU size for the connection, default:1500.'))
        parser.add_argument(
            '--initiator',
            default='bi-directional' if is_create else argparse.SUPPRESS,
            choices=['bi-directional', 'response-only'],
            help=_('Initiator state in lowercase, default:bi-directional'))

    def args2body(self, parsed_args, body=None):
        """Add in conditional args and then return all conn info."""

        if body is None:
            body = {}
        if parsed_args.dpd:
            vpn_utils.validate_dpd_dict(parsed_args.dpd)
            body['dpd'] = parsed_args.dpd
        if parsed_args.local_ep_group:
            _local_epg = neutronv20.find_resourceid_by_name_or_id(
                self.get_client(), 'endpoint_group',
                parsed_args.local_ep_group)
            body['local_ep_group_id'] = _local_epg
        if parsed_args.peer_ep_group:
            _peer_epg = neutronv20.find_resourceid_by_name_or_id(
                self.get_client(), 'endpoint_group',
                parsed_args.peer_ep_group)
            body['peer_ep_group_id'] = _peer_epg
        if hasattr(parsed_args, 'mtu') and int(parsed_args.mtu) < 68:
            message = _("Invalid MTU value: MTU must be "
                        "greater than or equal to 68.")
            raise exceptions.CommandError(message)
        # ToDo (Reedip) : Remove below check when peer-cidr is removed
        if parsed_args.peer_cidrs and parsed_args.local_ep_group:
            message = _("You cannot specify both endpoint groups and peer "
                        "CIDR(s).")
            raise exceptions.CommandError(message)
        neutronv20.update_dict(parsed_args, body,
                               ['peer_id', 'mtu', 'initiator', 'psk',
                                'peer_address', 'name', 'description',
                                'peer_cidrs'])
        return {self.resource: body}


class CreateIPsecSiteConnection(IPsecSiteConnectionMixin,
                                neutronv20.CreateCommand):
    """Create an IPsec site connection."""
    resource = 'ipsec_site_connection'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help=_('Set admin state up to false.'))
        parser.add_argument(
            '--vpnservice-id', metavar='VPNSERVICE',
            required=True,
            help=_('VPN service instance ID associated with this connection.'))
        parser.add_argument(
            '--ikepolicy-id', metavar='IKEPOLICY',
            required=True,
            help=_('IKE policy ID associated with this connection.'))
        parser.add_argument(
            '--ipsecpolicy-id', metavar='IPSECPOLICY',
            required=True,
            help=_('IPsec policy ID associated with this connection.'))
        super(CreateIPsecSiteConnection, self).add_known_arguments(parser)

    def args2body(self, parsed_args):
        _vpnservice_id = neutronv20.find_resourceid_by_name_or_id(
            self.get_client(), 'vpnservice',
            parsed_args.vpnservice_id)
        _ikepolicy_id = neutronv20.find_resourceid_by_name_or_id(
            self.get_client(), 'ikepolicy',
            parsed_args.ikepolicy_id)
        _ipsecpolicy_id = neutronv20.find_resourceid_by_name_or_id(
            self.get_client(), 'ipsecpolicy',
            parsed_args.ipsecpolicy_id)
        body = {
            'vpnservice_id': _vpnservice_id,
            'ikepolicy_id': _ikepolicy_id,
            'ipsecpolicy_id': _ipsecpolicy_id,
            'admin_state_up': parsed_args.admin_state_down,
        }
        if parsed_args.tenant_id:
            body['tenant_id'] = parsed_args.tenant_id

        if (bool(parsed_args.local_ep_group) !=
                bool(parsed_args.peer_ep_group)):
            message = _("You must specify both local and peer endpoint "
                        "groups.")
            raise exceptions.CommandError(message)
        if not parsed_args.peer_cidrs and not parsed_args.local_ep_group:
            message = _("You must specify endpoint groups or peer CIDR(s).")
            raise exceptions.CommandError(message)
        return super(CreateIPsecSiteConnection, self).args2body(parsed_args,
                                                                body)


class UpdateIPsecSiteConnection(IPsecSiteConnectionMixin,
                                neutronv20.UpdateCommand):
    """Update a given IPsec site connection."""

    resource = 'ipsec_site_connection'
    help_resource = 'IPsec site connection'

    def add_known_arguments(self, parser):
        utils.add_boolean_argument(
            parser, '--admin-state-up',
            help=_('Update the administrative state. (True meaning "Up")'))
        super(UpdateIPsecSiteConnection, self).add_known_arguments(parser,
                                                                   False)

    def args2body(self, parsed_args):
        body = {}
        neutronv20.update_dict(parsed_args, body, ['admin_state_up'])
        return super(UpdateIPsecSiteConnection, self).args2body(parsed_args,
                                                                body)


class DeleteIPsecSiteConnection(neutronv20.DeleteCommand):
    """Delete a given IPsec site connection."""

    resource = 'ipsec_site_connection'
    help_resource = 'IPsec site connection'
