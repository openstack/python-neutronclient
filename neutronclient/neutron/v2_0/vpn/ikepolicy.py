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

from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.vpn import utils as vpn_utils


class ListIKEPolicy(neutronv20.ListCommand):
    """List IKEPolicies that belong to a tenant."""

    resource = 'ikepolicy'
    log = logging.getLogger(__name__ + '.ListIKEPolicy')
    list_columns = ['id', 'name', 'auth_algorithm',
                    'encryption_algorithm', 'ike_version', 'pfs']
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowIKEPolicy(neutronv20.ShowCommand):
    """Show information of a given IKEPolicy."""

    resource = 'ikepolicy'
    log = logging.getLogger(__name__ + '.ShowIKEPolicy')


class CreateIKEPolicy(neutronv20.CreateCommand):
    """Create an IKEPolicy."""

    resource = 'ikepolicy'
    log = logging.getLogger(__name__ + '.CreateIKEPolicy')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help='Description of the IKE policy')
        parser.add_argument(
            '--auth-algorithm',
            default='sha1', choices=['sha1'],
            help='Authentication algorithm in lowercase. '
                 'default:sha1')
        parser.add_argument(
            '--encryption-algorithm',
            default='aes-128', choices=['3des',
                                        'aes-128',
                                        'aes-192',
                                        'aes-256'],
            help='Encryption Algorithm in lowercase, default:aes-128')
        parser.add_argument(
            '--phase1-negotiation-mode',
            default='main', choices=['main'],
            help='IKE Phase1 negotiation mode in lowercase, default:main')
        parser.add_argument(
            '--ike-version',
            default='v1', choices=['v1', 'v2'],
            help='IKE version in lowercase, default:v1')
        parser.add_argument(
            '--pfs',
            default='group5', choices=['group2', 'group5', 'group14'],
            help='Perfect Forward Secrecy in lowercase, default:group5')
        parser.add_argument(
            '--lifetime',
            metavar="units=UNITS,value=VALUE",
            type=utils.str2dict,
            help=vpn_utils.lifetime_help("IKE"))
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of the IKE Policy')

    def args2body(self, parsed_args):

        body = {'ikepolicy': {
            'auth_algorithm': parsed_args.auth_algorithm,
            'encryption_algorithm': parsed_args.encryption_algorithm,
            'phase1_negotiation_mode': parsed_args.phase1_negotiation_mode,
            'ike_version': parsed_args.ike_version,
            'pfs': parsed_args.pfs,
        }, }
        if parsed_args.name:
            body['ikepolicy'].update({'name': parsed_args.name})
        if parsed_args.description:
            body['ikepolicy'].update({'description': parsed_args.description})
        if parsed_args.tenant_id:
            body['ikepolicy'].update({'tenant_id': parsed_args.tenant_id})
        if parsed_args.lifetime:
            vpn_utils.validate_lifetime_dict(parsed_args.lifetime)
            body['ikepolicy'].update({'lifetime': parsed_args.lifetime})
        return body


class UpdateIKEPolicy(neutronv20.UpdateCommand):
    """Update a given IKE Policy."""

    resource = 'ikepolicy'
    log = logging.getLogger(__name__ + '.UpdateIKEPolicy')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--lifetime',
            metavar="units=UNITS,value=VALUE",
            type=utils.str2dict,
            help=vpn_utils.lifetime_help("IKE"))

    def args2body(self, parsed_args):

        body = {'ikepolicy': {
        }, }
        if parsed_args.lifetime:
            vpn_utils.validate_lifetime_dict(parsed_args.lifetime)
            body['ikepolicy'].update({'lifetime': parsed_args.lifetime})
        return body


class DeleteIKEPolicy(neutronv20.DeleteCommand):
    """Delete a given IKE Policy."""

    resource = 'ikepolicy'
    log = logging.getLogger(__name__ + '.DeleteIKEPolicy')
