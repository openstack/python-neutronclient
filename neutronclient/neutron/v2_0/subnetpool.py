# Copyright 2015 OpenStack Foundation.
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

from neutronclient.i18n import _
from neutronclient.neutron import v2_0 as neutronV20


def add_updatable_arguments(parser):
    parser.add_argument(
        '--min-prefixlen', type=int,
        help=_('Subnetpool minimum prefix length.'))
    parser.add_argument(
        '--max-prefixlen', type=int,
        help=_('Subnetpool maximum prefix length.'))
    parser.add_argument(
        '--default-prefixlen', type=int,
        help=_('Subnetpool default prefix length.'))
    parser.add_argument(
        '--pool-prefix',
        action='append', dest='prefixes',
        help=_('Subnetpool prefixes (This option can be repeated).'))


def updatable_args2body(parsed_args, body, for_create=True):
    neutronV20.update_dict(parsed_args, body['subnetpool'],
                           ['name', 'prefixes', 'default_prefixlen',
                            'min_prefixlen', 'max_prefixlen'])


class ListSubnetPool(neutronV20.ListCommand):
    """List subnetpools that belong to a given tenant."""

    resource = 'subnetpool'
    list_columns = ['id', 'name', 'prefixes',
                    'default_prefixlen', 'address_scope_id']
    pagination_support = True
    sorting_support = True


class ShowSubnetPool(neutronV20.ShowCommand):
    """Show information of a given subnetpool."""

    resource = 'subnetpool'


class CreateSubnetPool(neutronV20.CreateCommand):
    """Create a subnetpool for a given tenant."""

    resource = 'subnetpool'

    def add_known_arguments(self, parser):
        add_updatable_arguments(parser)
        parser.add_argument(
            '--shared',
            action='store_true',
            help=_('Set the subnetpool as shared.'))
        parser.add_argument(
            'name',
            help=_('Name of subnetpool to create.'))
        parser.add_argument(
            '--address-scope',
            metavar='ADDRSCOPE',
            help=_('ID or name of the address scope with which the subnetpool '
                   'is associated. Prefixes must be unique across address '
                   'scopes'))

    def args2body(self, parsed_args):
        body = {'subnetpool': {'prefixes': parsed_args.prefixes}}
        updatable_args2body(parsed_args, body)
        if parsed_args.shared:
            body['subnetpool']['shared'] = True

        # Parse and update for "address-scope" option
        if parsed_args.address_scope:
            _addrscope_id = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'address_scope',
                parsed_args.address_scope)
            body['subnetpool']['address_scope_id'] = _addrscope_id
        return body


class DeleteSubnetPool(neutronV20.DeleteCommand):
    """Delete a given subnetpool."""

    resource = 'subnetpool'


class UpdateSubnetPool(neutronV20.UpdateCommand):
    """Update subnetpool's information."""

    resource = 'subnetpool'

    def add_known_arguments(self, parser):
        add_updatable_arguments(parser)
        parser.add_argument('--name',
                            help=_('Name of subnetpool to update.'))
        addrscope_args = parser.add_mutually_exclusive_group()
        addrscope_args.add_argument('--address-scope',
                                    metavar='ADDRSCOPE',
                                    help=_('ID or name of the address scope '
                                           'with which the subnetpool is '
                                           'associated. Prefixes must be '
                                           'unique across address scopes'))
        addrscope_args.add_argument('--no-address-scope',
                                    action='store_true',
                                    help=_('Detach subnetpool from the '
                                           'address scope'))

    def args2body(self, parsed_args):
        body = {'subnetpool': {}}
        updatable_args2body(parsed_args, body, for_create=False)

        # Parse and update for "address-scope" option/s
        if parsed_args.no_address_scope:
            body['subnetpool']['address_scope_id'] = None
        elif parsed_args.address_scope:
            _addrscope_id = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'address_scope',
                parsed_args.address_scope)
            body['subnetpool']['address_scope_id'] = _addrscope_id
        return body
