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
                    'default_prefixlen']
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

    def args2body(self, parsed_args):
        body = {'subnetpool': {'prefixes': parsed_args.prefixes}}
        updatable_args2body(parsed_args, body)
        if parsed_args.shared:
            body['subnetpool']['shared'] = True
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

    def args2body(self, parsed_args):
        body = {'subnetpool': {}}
        updatable_args2body(parsed_args, body, for_create=False)
        return body
