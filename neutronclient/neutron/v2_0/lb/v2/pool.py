# Copyright 2013 Mirantis Inc.
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

from neutronclient.common import utils
from neutronclient.i18n import _
from neutronclient.neutron import v2_0 as neutronV20


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
            help=_('The type of session persistence to use and associated '
                   'cookie name'))
        parser.add_argument(
            '--name', help=_('The name of the pool.'))
        parser.add_argument(
            '--lb-algorithm',
            required=True,
            choices=['ROUND_ROBIN', 'LEAST_CONNECTIONS', 'SOURCE_IP'],
            help=_('The algorithm used to distribute load between the members '
                   'of the pool.'))
        parser.add_argument(
            '--listener',
            required=True,
            help=_('The listener to associate with the pool'))
        parser.add_argument(
            '--protocol',
            required=True,
            choices=['HTTP', 'HTTPS', 'TCP'],
            help=_('Protocol for balancing.'))

    def args2body(self, parsed_args):
        if parsed_args.session_persistence:
            parsed_args.session_persistence = utils.str2dict(
                parsed_args.session_persistence)
        _listener_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'listener', parsed_args.listener)
        body = {
            self.resource: {
                'admin_state_up': parsed_args.admin_state,
                'protocol': parsed_args.protocol,
                'lb_algorithm': parsed_args.lb_algorithm,
                'listener_id': _listener_id,
            },
        }
        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['description', 'name',
                                'session_persistence'])
        return body


class UpdatePool(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'


class DeletePool(neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'
