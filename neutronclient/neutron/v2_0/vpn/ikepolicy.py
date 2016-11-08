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
        '--description',
        help=_('Description of the IKE policy.'))
    parser.add_argument(
        '--auth-algorithm',
        type=utils.convert_to_lowercase,
        default='sha1' if is_create else argparse.SUPPRESS,
        choices=['sha1', 'sha256', 'sha384', 'sha512'],
        help=_('Authentication algorithm, default:sha1.'))
    parser.add_argument(
        '--encryption-algorithm',
        default='aes-128' if is_create else argparse.SUPPRESS,
        type=utils.convert_to_lowercase,
        help=_('Encryption algorithm, default:aes-128.'))
    parser.add_argument(
        '--phase1-negotiation-mode',
        default='main' if is_create else argparse.SUPPRESS,
        choices=['main'],
        type=utils.convert_to_lowercase,
        help=_('IKE Phase1 negotiation mode, default:main.'))
    parser.add_argument(
        '--ike-version',
        default='v1' if is_create else argparse.SUPPRESS,
        choices=['v1', 'v2'],
        type=utils.convert_to_lowercase,
        help=_('IKE version for the policy, default:v1.'))
    parser.add_argument(
        '--pfs',
        default='group5' if is_create else argparse.SUPPRESS,
        type=utils.convert_to_lowercase,
        help=_('Perfect Forward Secrecy, default:group5.'))
    parser.add_argument(
        '--lifetime',
        metavar="units=UNITS,value=VALUE",
        type=utils.str2dict_type(optional_keys=['units', 'value']),
        help=vpn_utils.lifetime_help("IKE"))


def parse_common_args2body(parsed_args, body):
    neutronv20.update_dict(parsed_args, body,
                           ['auth_algorithm', 'encryption_algorithm',
                            'phase1_negotiation_mode', 'ike_version',
                            'pfs', 'name', 'description', 'tenant_id'])
    if parsed_args.lifetime:
        vpn_utils.validate_lifetime_dict(parsed_args.lifetime)
        body['lifetime'] = parsed_args.lifetime
    return body


class ListIKEPolicy(neutronv20.ListCommand):
    """List IKE policies that belong to a tenant."""

    resource = 'ikepolicy'
    list_columns = ['id', 'name', 'auth_algorithm',
                    'encryption_algorithm', 'ike_version', 'pfs']
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowIKEPolicy(neutronv20.ShowCommand):
    """Show information of a given IKE policy."""

    resource = 'ikepolicy'
    help_resource = 'IKE policy'


class CreateIKEPolicy(neutronv20.CreateCommand):
    """Create an IKE policy."""

    resource = 'ikepolicy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of the IKE policy.'))
        add_common_args(parser)

    def args2body(self, parsed_args):
        return {'ikepolicy': parse_common_args2body(parsed_args, body={})}


class UpdateIKEPolicy(neutronv20.UpdateCommand):
    """Update a given IKE policy."""

    resource = 'ikepolicy'
    help_resource = 'IKE policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Updated name of the IKE policy.'))
        add_common_args(parser, is_create=False)

    def args2body(self, parsed_args):
        return {'ikepolicy': parse_common_args2body(parsed_args, body={})}


class DeleteIKEPolicy(neutronv20.DeleteCommand):
    """Delete a given IKE policy."""

    resource = 'ikepolicy'
    help_resource = 'IKE policy'
