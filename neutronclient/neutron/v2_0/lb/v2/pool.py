# Copyright 2013 Mirantis Inc.
# Copyright 2014 Blue Box Group, Inc.
# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2015 Blue Box, an IBM Company
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


def _get_listener(client, listener_id_or_name):
    return neutronV20.find_resource_by_name_or_id(
        client, 'listener', listener_id_or_name)


def _get_listener_id(client, listener_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(
        client, 'listener', listener_id_or_name)


class ListPool(neutronV20.ListCommand):
    """LBaaS v2 List pools that belong to a given tenant."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'
    list_columns = ['id', 'name', 'lb_method', 'protocol',
                    'admin_state_up']
    pagination_support = True
    sorting_support = True


class ShowPool(neutronV20.ShowCommand):
    """LBaaS v2 Show information of a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'

    def cleanup_output_data(self, data):
        if 'members' not in data['pool']:
            return []
        member_info = []
        for member in data['pool']['members']:
            member_info.append(member['id'])
        data['pool']['members'] = member_info


class CreatePool(neutronV20.CreateCommand):
    """LBaaS v2 Create a pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false.'))
        parser.add_argument(
            '--description',
            help=_('Description of the pool.'))
        parser.add_argument(
            '--session-persistence',
            metavar='type=TYPE[,cookie_name=COOKIE_NAME]',
            type=utils.str2dict_type(required_keys=['type'],
                                     optional_keys=['cookie_name']),
            help=_('The type of session persistence to use and associated '
                   'cookie name'))
        parser.add_argument(
            '--name', help=_('The name of the pool.'))
        parser.add_argument(
            '--listener',
            help=_('Listener whose default-pool should be set to this pool. '
                   'At least one of --listener or --loadbalancer must be '
                   'specified.'))
        parser.add_argument(
            '--loadbalancer',
            help=_('Loadbalancer with which this pool should be associated. '
                   'At least one of --listener or --loadbalancer must be '
                   'specified.'))
        parser.add_argument(
            '--lb-algorithm',
            required=True,
            choices=['ROUND_ROBIN', 'LEAST_CONNECTIONS', 'SOURCE_IP'],
            help=_('The algorithm used to distribute load between the members '
                   'of the pool.'))
        parser.add_argument(
            '--protocol',
            required=True,
            choices=['HTTP', 'HTTPS', 'TCP'],
            type=utils.convert_to_uppercase,
            help=_('Protocol for balancing.'))

    def args2body(self, parsed_args):
        resource = {
            'admin_state_up': parsed_args.admin_state,
            'protocol': parsed_args.protocol,
            'lb_algorithm': parsed_args.lb_algorithm
        }
        if not parsed_args.listener and not parsed_args.loadbalancer:
            message = _('At least one of --listener or --loadbalancer must be '
                        'specified.')
            raise exceptions.CommandError(message)
        if parsed_args.listener:
            listener_id = _get_listener_id(
                self.get_client(),
                parsed_args.listener)
            resource['listener_id'] = listener_id
        if parsed_args.loadbalancer:
            loadbalancer_id = _get_loadbalancer_id(
                self.get_client(),
                parsed_args.loadbalancer)
            resource['loadbalancer_id'] = loadbalancer_id
        neutronV20.update_dict(parsed_args, resource,
                               ['description', 'name',
                                'session_persistence', 'tenant_id'])
        return {self.resource: resource}


class UpdatePool(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'


class DeletePool(neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'
