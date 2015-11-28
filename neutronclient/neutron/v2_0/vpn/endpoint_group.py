#    (c) Copyright 2015 Cisco Systems, Inc.
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

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronv20


def add_known_endpoint_group_arguments(parser, is_create=True):
    parser.add_argument(
        '--name',
        help=_('Set a name for the endpoint group.'))
    parser.add_argument(
        '--description',
        help=_('Set a description for the endpoint group.'))
    if is_create:
        parser.add_argument(
            '--type',
            required=is_create,
            help=_('Type of endpoints in group (e.g. subnet, cidr, vlan).'))
        parser.add_argument(
            '--value',
            action='append', dest='endpoints',
            required=is_create,
            help=_('Endpoint(s) for the group. Must all be of the same type.'))


class ListEndpointGroup(neutronv20.ListCommand):
    """List VPN endpoint groups that belong to a given tenant."""

    resource = 'endpoint_group'
    list_columns = ['id', 'name', 'type', 'endpoints']
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowEndpointGroup(neutronv20.ShowCommand):
    """Show a specific VPN endpoint group."""

    resource = 'endpoint_group'


class CreateEndpointGroup(neutronv20.CreateCommand):
    """Create a VPN endpoint group."""
    resource = 'endpoint_group'

    def add_known_arguments(self, parser):
        add_known_endpoint_group_arguments(parser)

    def subnet_name2id(self, endpoint):
        return neutronv20.find_resourceid_by_name_or_id(self.get_client(),
                                                        'subnet', endpoint)

    def args2body(self, parsed_args):
        if parsed_args.type == 'subnet':
            endpoints = [self.subnet_name2id(ep)
                         for ep in parsed_args.endpoints]
        else:
            endpoints = parsed_args.endpoints

        body = {'endpoints': endpoints}

        neutronv20.update_dict(parsed_args, body,
                               ['name', 'description',
                                'tenant_id', 'type'])
        return {self.resource: body}


class UpdateEndpointGroup(neutronv20.UpdateCommand):
    """Update a given VPN endpoint group."""

    resource = 'endpoint_group'

    def add_known_arguments(self, parser):
        add_known_endpoint_group_arguments(parser, is_create=False)

    def args2body(self, parsed_args):
        body = {}
        neutronv20.update_dict(parsed_args, body,
                               ['name', 'description'])
        return {self.resource: body}


class DeleteEndpointGroup(neutronv20.DeleteCommand):
    """Delete a given VPN endpoint group."""

    resource = 'endpoint_group'
