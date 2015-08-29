# Copyright 2014 Blue Box Group, Inc.
# Copyright 2015 Hewlett-Packard Development Company, L.P.
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

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


def _get_loadbalancer_id(client, lb_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(
        client, 'loadbalancer', lb_id_or_name,
        cmd_resource='lbaas_loadbalancer')


def _get_pool(client, pool_id_or_name):
    return neutronV20.find_resource_by_name_or_id(
        client, 'pool', pool_id_or_name, cmd_resource='lbaas_pool')


def _get_pool_id(client, pool_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(
        client, 'pool', pool_id_or_name, cmd_resource='lbaas_pool')


class ListListener(neutronV20.ListCommand):
    """LBaaS v2 List listeners that belong to a given tenant."""

    resource = 'listener'
    list_columns = ['id', 'default_pool_id', 'name', 'protocol',
                    'protocol_port', 'admin_state_up', 'status']
    pagination_support = True
    sorting_support = True


class ShowListener(neutronV20.ShowCommand):
    """LBaaS v2 Show information of a given listener."""

    resource = 'listener'


class CreateListener(neutronV20.CreateCommand):
    """LBaaS v2 Create a listener."""

    resource = 'listener'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false.'))
        parser.add_argument(
            '--connection-limit',
            help=_('The maximum number of connections per second allowed for '
                   'the vip. Positive integer or -1 for unlimited (default).'),
            type=int)
        parser.add_argument(
            '--description',
            help=_('Description of the listener.'))
        parser.add_argument(
            '--name',
            help=_('The name of the listener. At least one of --default-pool '
                   'or --loadbalancer must be specified.'))
        parser.add_argument(
            '--default-tls-container-ref',
            dest='default_tls_container_ref',
            help=_('Default TLS container reference'
                   ' to retrieve TLS information.'))
        parser.add_argument(
            '--sni-container-refs',
            dest='sni_container_refs',
            nargs='+',
            help=_('List of TLS container references for SNI.'))
        parser.add_argument(
            '--default-pool',
            help=_('Default pool for the listener.'))
        parser.add_argument(
            '--loadbalancer',
            metavar='LOADBALANCER',
            help=_('ID or name of the load balancer.'))
        parser.add_argument(
            '--protocol',
            required=True,
            choices=['TCP', 'HTTP', 'HTTPS', 'TERMINATED_HTTPS'],
            type=utils.convert_to_uppercase,
            help=_('Protocol for the listener.'))
        parser.add_argument(
            '--protocol-port',
            dest='protocol_port', required=True,
            metavar='PORT',
            help=_('Protocol port for the listener.'))

    def args2body(self, parsed_args):
        resource = {
            'protocol': parsed_args.protocol,
            'protocol_port': parsed_args.protocol_port,
            'admin_state_up': parsed_args.admin_state
        }
        if not parsed_args.loadbalancer and not parsed_args.default_pool:
            message = _('Either --default-pool or --loadbalancer must be '
                        'specified.')
            raise exceptions.CommandError(message)
        if parsed_args.loadbalancer:
            loadbalancer_id = _get_loadbalancer_id(
                self.get_client(), parsed_args.loadbalancer)
            resource['loadbalancer_id'] = loadbalancer_id
        if parsed_args.default_pool:
            default_pool_id = _get_pool_id(
                self.get_client(), parsed_args.default_pool)
            resource['default_pool_id'] = default_pool_id

        neutronV20.update_dict(parsed_args, resource,
                               ['connection_limit', 'description',
                                'name', 'default_tls_container_ref',
                                'sni_container_refs', 'tenant_id'])
        return {self.resource: resource}


class UpdateListener(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given listener."""

    resource = 'listener'
    allow_names = False


class DeleteListener(neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given listener."""

    resource = 'listener'
