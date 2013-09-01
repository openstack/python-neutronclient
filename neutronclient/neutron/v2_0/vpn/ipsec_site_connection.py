# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
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
# @author: Swaminathan Vasudevan, Hewlett-Packard.
#

import logging

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.vpn import utils as vpn_utils
from neutronclient.openstack.common.gettextutils import _


def _format_peer_cidrs(ipsec_site_connection):
    try:
        return '\n'.join([utils.dumps(cidrs) for cidrs in
                          ipsec_site_connection['peer_cidrs']])
    except Exception:
        return ''


class ListIPsecSiteConnection(neutronv20.ListCommand):
    """List IPsecSiteConnections that belong to a given tenant."""

    resource = 'ipsec_site_connection'
    log = logging.getLogger(__name__ + '.ListIPsecSiteConnection')
    _formatters = {'peer_cidrs': _format_peer_cidrs}
    list_columns = [
        'id', 'name', 'peer_address', 'peer_cidrs', 'route_mode',
        'auth_mode', 'status']
    pagination_support = True
    sorting_support = True


class ShowIPsecSiteConnection(neutronv20.ShowCommand):
    """Show information of a given IPsecSiteConnection."""

    resource = 'ipsec_site_connection'
    log = logging.getLogger(__name__ + '.ShowIPsecSiteConnection')


class CreateIPsecSiteConnection(neutronv20.CreateCommand):
    """Create an IPsecSiteConnection."""
    resource = 'ipsec_site_connection'
    log = logging.getLogger(__name__ + '.CreateIPsecSiteConnection')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='Set admin state up to false')
        parser.add_argument(
            '--name',
            help='Set friendly name for the connection')
        parser.add_argument(
            '--description',
            help='Set a description for the connection')
        parser.add_argument(
            '--mtu',
            default='1500',
            help='MTU size for the connection, default:1500')
        parser.add_argument(
            '--initiator',
            default='bi-directional', choices=['bi-directional',
                                               'response-only'],
            help='Initiator state in lowercase, default:bi-directional')
        parser.add_argument(
            '--dpd',
            metavar="action=ACTION,interval=INTERVAL,timeout=TIMEOUT",
            type=utils.str2dict,
            help=vpn_utils.dpd_help("IPsec Connection"))
        parser.add_argument(
            '--vpnservice-id', metavar='VPNSERVICE',
            required=True,
            help='VPNService instance id associated with this connection')
        parser.add_argument(
            '--ikepolicy-id', metavar='IKEPOLICY',
            required=True,
            help='IKEPolicy id associated with this connection')
        parser.add_argument(
            '--ipsecpolicy-id', metavar='IPSECPOLICY',
            required=True,
            help='IPsecPolicy id associated with this connection')
        parser.add_argument(
            '--peer-address',
            required=True,
            help='Remote branch router public '
                 'IPv4 address or IPv6 address or FQDN.')
        parser.add_argument(
            '--peer-id',
            required=True,
            help='Remote branch router identity')
        parser.add_argument(
            '--peer-cidr',
            action='append', dest='peer_cidrs',
            required=True,
            help='Remote subnet(s) in CIDR format')
        parser.add_argument(
            '--psk',
            required=True,
            help='Pre-Shared Key string')

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
        if int(parsed_args.mtu) < 68:
            message = _("Invalid MTU value: MTU must be "
                        "greater than or equal to 68")
            raise exceptions.CommandError(message)
        body = {'ipsec_site_connection': {
            'vpnservice_id': _vpnservice_id,
            'ikepolicy_id': _ikepolicy_id,
            'ipsecpolicy_id': _ipsecpolicy_id,
            'peer_address': parsed_args.peer_address,
            'peer_id': parsed_args.peer_id,
            'mtu': parsed_args.mtu,
            'initiator': parsed_args.initiator,
            'psk': parsed_args.psk,
            'admin_state_up': parsed_args.admin_state_down,
        }, }
        if parsed_args.name:
            body['ipsec_site_connection'].update(
                {'name': parsed_args.name}
            )
        if parsed_args.description:
            body['ipsec_site_connection'].update(
                {'description': parsed_args.description}
            )
        if parsed_args.tenant_id:
            body['ipsec_site_connection'].update(
                {'tenant_id': parsed_args.tenant_id}
            )
        if parsed_args.dpd:
            vpn_utils.validate_dpd_dict(parsed_args.dpd)
            body['ipsec_site_connection'].update({'dpd': parsed_args.dpd})
        if parsed_args.peer_cidrs:
            body['ipsec_site_connection'][
                'peer_cidrs'] = parsed_args.peer_cidrs

        return body


class UpdateIPsecSiteConnection(neutronv20.UpdateCommand):
    """Update a given IPsecSiteConnection."""

    resource = 'ipsec_site_connection'
    log = logging.getLogger(__name__ + '.UpdateIPsecSiteConnection')

    def add_known_arguments(self, parser):

        parser.add_argument(
            '--dpd',
            metavar="action=ACTION,interval=INTERVAL,timeout=TIMEOUT",
            type=utils.str2dict,
            help=vpn_utils.dpd_help("IPsec Connection"))

    def args2body(self, parsed_args):
        body = {'ipsec_site_connection': {
        }, }

        if parsed_args.dpd:
            vpn_utils.validate_dpd_dict(parsed_args.dpd)
            body['ipsec_site_connection'].update({'dpd': parsed_args.dpd})
        return body


class DeleteIPsecSiteConnection(neutronv20.DeleteCommand):
    """Delete a given IPsecSiteConnection."""

    resource = 'ipsec_site_connection'
    log = logging.getLogger(__name__ + '.DeleteIPsecSiteConnection')
