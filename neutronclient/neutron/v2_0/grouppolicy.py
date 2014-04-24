# Copyright 2012 OpenStack Foundation.
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

import logging
import string

from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


class ListEndpoint(neutronV20.ListCommand):
    """List endpoints that belong to a given tenant."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.ListEndpoint')
    _formatters = {}
    list_columns = ['id', 'name', 'description']
    pagination_support = True
    sorting_support = True


class ShowEndpoint(neutronV20.ShowCommand):
    """Show information of a given endpoint."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.ShowEndpoint')


class UpdateEndpointPortMixin(object):
    def add_arguments_port(self, parser):
        parser.add_argument(
            '--port',
            default='',
            help=_('Port uuid'))

    def args2body_port(self, parsed_args, endpoint):
        if parsed_args.port:
            endpoint['port'] = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'port', parsed_args.port)


class CreateEndpoint(neutronV20.CreateCommand, UpdateEndpointPortMixin):
    """Create a endpoint for a given tenant."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.CreateEndpoint')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the endpoint'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of endpoint to create'))

        self.add_arguments_port(parser)

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description'])

        self.args2body_port(parsed_args, body[self.resource])

        return body


class DeleteEndpoint(neutronV20.DeleteCommand):
    """Delete a given endpoint."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.DeleteEndpoint')


class UpdateEndpoint(neutronV20.UpdateCommand):
    """Update endpoint's information."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.UpdateEndpoint')


def _format_endpoints(endpoint_group):
    out = '\n'.join([endpoint for endpoint in endpoint_group['endpoints']])
    return out


class ListEndpointGroup(neutronV20.ListCommand):
    """List endpoint_groups that belong to a given tenant."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.ListEndpointGroup')
    list_columns = ['id', 'name', 'description', 'parent_id',
                    'endpoints']
    _formatters = {'endpoints': _format_endpoints, }
    pagination_support = True
    sorting_support = True


class ShowEndpointGroup(neutronV20.ShowCommand):
    """Show information of a given endpoint_group."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.ShowEndpointGroup')


class UpdateEndpointGroupSubnetMixin(object):
    def add_arguments_subnet(self, parser):
        parser.add_argument(
            '--subnet',
            default='',
            help=_('Subnet uuid'))

    def args2body_subnet(self, parsed_args, endpoint):
        if parsed_args.subnet:
            endpoint['subnet'] = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'subnet', parsed_args.subnet)


class CreateEndpointGroup(neutronV20.CreateCommand,
                          UpdateEndpointGroupSubnetMixin):
    """Create a endpoint_group for a given tenant."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.CreateEndpointGroup')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the endpoint_group'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of endpoint_group to create'))
        parser.add_argument(
            '--parent_id', metavar='PARENT EPG',
            help=_('Parent endpoint_group uuid'))
        parser.add_argument(
            '--endpoints', type=string.split,
            default=[],
            help=_('Parent endpoint_group uuid'))
        parser.add_argument(
            '--provided_contract_scopes', type=string.split,
            default=[],
            help=_('Parent endpoint_group uuid'))
        parser.add_argument(
            '--consumed_contract_scopes', type=string.split,
            default=[],
            help=_('Parent endpoint_group uuid'))

        self.add_arguments_subnet(parser)

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        attr_map = {'endpoints': 'endpoint',
                    'provided_contract_scopes': 'contract_scope',
                    'consumed_contract_scopes': 'contract_scope'}
        for attr_name, res_name in attr_map.items():
            if getattr(parsed_args, attr_name):
                _uuids = [
                    neutronV20.find_resourceid_by_name_or_id(
                        self.get_client(),
                        res_name,
                        elem) for elem in getattr(parsed_args, attr_name)]
                body[self.resource][attr_name] = _uuids

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description',
                                'parent_id'])

        self.args2body_subnet(parsed_args, body[self.resource])

        return body


class DeleteEndpointGroup(neutronV20.DeleteCommand):
    """Delete a given endpoint_group."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.DeleteEndpointGroup')


class UpdateEndpointGroup(neutronV20.UpdateCommand):
    """Update endpoint_group's information."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.UpdateEndpointGroup')
