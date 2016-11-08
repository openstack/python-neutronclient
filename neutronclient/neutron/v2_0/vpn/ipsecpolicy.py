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

from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.vpn import utils as vpn_utils


def add_common_args(parser, is_create=True):
    parser.add_argument(
        '--auth-algorithm',
        default='sha1' if is_create else argparse.SUPPRESS,
        type=utils.convert_to_lowercase,
        choices=['sha1', 'sha256', 'sha384', 'sha512'],
        help=_('Authentication algorithm for IPsec policy, default:sha1.'))
    parser.add_argument(
        '--description',
        help=_('Description of the IPsec policy.'))
    parser.add_argument(
        '--encapsulation-mode',
        default='tunnel' if is_create else argparse.SUPPRESS,
        choices=['tunnel', 'transport'],
        type=utils.convert_to_lowercase,
        help=_('Encapsulation mode for IPsec policy, default:tunnel.'))
    parser.add_argument(
        '--encryption-algorithm',
        default='aes-128' if is_create else argparse.SUPPRESS,
        type=utils.convert_to_lowercase,
        help=_('Encryption algorithm for IPsec policy, default:aes-128.'))
    parser.add_argument(
        '--lifetime',
        metavar="units=UNITS,value=VALUE",
        type=utils.str2dict_type(optional_keys=['units', 'value']),
        help=vpn_utils.lifetime_help("IPsec"))
    parser.add_argument(
        '--pfs',
        default='group5' if is_create else argparse.SUPPRESS,
        type=utils.convert_to_lowercase,
        help=_('Perfect Forward Secrecy for IPsec policy, default:group5.'))
    parser.add_argument(
        '--transform-protocol',
        default='esp' if is_create else argparse.SUPPRESS,
        type=utils.convert_to_lowercase,
        choices=['esp', 'ah', 'ah-esp'],
        help=_('Transform protocol for IPsec policy, default:esp.'))


def parse_common_args2body(parsed_args, body):
    neutronv20.update_dict(parsed_args, body,
                           ['auth_algorithm', 'encryption_algorithm',
                            'encapsulation_mode', 'transform_protocol',
                            'pfs', 'name', 'description', 'tenant_id'])
    if parsed_args.lifetime:
        vpn_utils.validate_lifetime_dict(parsed_args.lifetime)
        body['lifetime'] = parsed_args.lifetime
    return body


class ListIPsecPolicy(neutronv20.ListCommand):
    """List IPsec policies that belong to a given tenant connection."""

    resource = 'ipsecpolicy'
    list_columns = ['id', 'name', 'auth_algorithm',
                    'encryption_algorithm', 'pfs']
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowIPsecPolicy(neutronv20.ShowCommand):
    """Show information of a given IPsec policy."""

    resource = 'ipsecpolicy'
    help_resource = 'IPsec policy'


class CreateIPsecPolicy(neutronv20.CreateCommand):
    """Create an IPsec policy."""

    resource = 'ipsecpolicy'
    help_resource = 'IPsec policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of the IPsec policy.'))
        add_common_args(parser)

    def args2body(self, parsed_args):
        return {'ipsecpolicy': parse_common_args2body(parsed_args, body={})}


class UpdateIPsecPolicy(neutronv20.UpdateCommand):
    """Update a given IPsec policy."""

    resource = 'ipsecpolicy'
    help_resource = 'IPsec policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Updated name of the IPsec policy.'))
        add_common_args(parser, is_create=False)

    def args2body(self, parsed_args):
        return {'ipsecpolicy': parse_common_args2body(parsed_args, body={})}


class DeleteIPsecPolicy(neutronv20.DeleteCommand):
    """Delete a given IPsec policy."""

    resource = 'ipsecpolicy'
    help_resource = 'IPsec policy'
