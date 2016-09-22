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


def _add_common_args(parser):
    parser.add_argument(
        '--description',
        help=_('Description of the listener.'))
    parser.add_argument(
        '--connection-limit',
        type=int,
        help=_('The maximum number of connections per second allowed for '
               'the listener. Positive integer or -1 '
               'for unlimited (default).'))
    parser.add_argument(
        '--default-pool',
        help=_('Default pool for the listener.'))


def _parse_common_args(body, parsed_args, client):
    neutronV20.update_dict(parsed_args, body,
                           ['name', 'description', 'connection_limit'])
    if parsed_args.default_pool:
        default_pool_id = _get_pool_id(
            client, parsed_args.default_pool)
        body['default_pool_id'] = default_pool_id


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
        _add_common_args(parser)
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false.'))
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
        if not parsed_args.loadbalancer and not parsed_args.default_pool:
            message = _('Either --default-pool or --loadbalancer must be '
                        'specified.')
            raise exceptions.CommandError(message)
        body = {
            'protocol': parsed_args.protocol,
            'protocol_port': parsed_args.protocol_port,
            'admin_state_up': parsed_args.admin_state
        }
        if parsed_args.loadbalancer:
            loadbalancer_id = _get_loadbalancer_id(
                self.get_client(), parsed_args.loadbalancer)
            body['loadbalancer_id'] = loadbalancer_id

        neutronV20.update_dict(parsed_args, body,
                               ['default_tls_container_ref',
                                'sni_container_refs', 'tenant_id'])
        _parse_common_args(body, parsed_args, self.get_client())
        return {self.resource: body}


class UpdateListener(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given listener."""

    resource = 'listener'

    def add_known_arguments(self, parser):
        _add_common_args(parser)
        parser.add_argument(
            '--name',
            help=_('Name of the listener.'))
        utils.add_boolean_argument(
            parser, '--admin-state-up', dest='admin_state_up',
            help=_('Specify the administrative state of the listener. '
                   '(True meaning "Up")'))

    def args2body(self, parsed_args):
        body = {}
        neutronV20.update_dict(parsed_args, body,
                               ['admin_state_up'])
        _parse_common_args(body, parsed_args, self.get_client())
        return {self.resource: body}


class DeleteListener(neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given listener."""

    resource = 'listener'
