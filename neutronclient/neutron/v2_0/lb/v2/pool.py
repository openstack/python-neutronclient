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


def _add_common_args(parser, is_create=True):
    parser.add_argument(
        '--description',
        help=_('Description of the pool.'))
    parser.add_argument(
        '--name', help=_('The name of the pool.'))
    parser.add_argument(
        '--lb-algorithm',
        required=is_create,
        type=utils.convert_to_uppercase,
        choices=['ROUND_ROBIN', 'LEAST_CONNECTIONS', 'SOURCE_IP'],
        help=_('The algorithm used to distribute load between the members '
               'of the pool.'))


def _parse_common_args(parsed_args):
    body = {}
    neutronV20.update_dict(parsed_args,
                           body, ['description', 'lb_algorithm', 'name'])
    return body


class ListPool(neutronV20.ListCommand):
    """LBaaS v2 List pools that belong to a given tenant."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'
    list_columns = ['id', 'name', 'lb_algorithm', 'protocol',
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
        _add_common_args(parser)
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false.'))
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
            '--protocol',
            type=utils.convert_to_uppercase,
            required=True,
            choices=['HTTP', 'HTTPS', 'TCP'],
            help=_('Protocol for balancing.'))
        parser.add_argument(
            '--session-persistence',
            metavar='type=TYPE[,cookie_name=COOKIE_NAME]',
            type=utils.str2dict_type(required_keys=['type'],
                                     optional_keys=['cookie_name']),
            help=_('The type of session persistence to use and associated '
                   'cookie name.'))

    def args2body(self, parsed_args):
        if not parsed_args.listener and not parsed_args.loadbalancer:
            message = _('At least one of --listener or --loadbalancer must be '
                        'specified.')
            raise exceptions.CommandError(message)
        body = _parse_common_args(parsed_args)
        if parsed_args.listener:
            listener_id = _get_listener_id(
                self.get_client(),
                parsed_args.listener)
            body['listener_id'] = listener_id
        if parsed_args.loadbalancer:
            loadbalancer_id = _get_loadbalancer_id(
                self.get_client(),
                parsed_args.loadbalancer)
            body['loadbalancer_id'] = loadbalancer_id
        body['admin_state_up'] = parsed_args.admin_state
        neutronV20.update_dict(parsed_args, body,
                               ['tenant_id', 'protocol',
                                'session_persistence'])
        return {self.resource: body}


class UpdatePool(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'

    def add_known_arguments(self, parser):
        utils.add_boolean_argument(
            parser, '--admin-state-up',
            help=_('Update the administrative state of '
                   'the pool (True meaning "Up").'))
        session_group = parser.add_mutually_exclusive_group()
        session_group.add_argument(
            '--session-persistence',
            metavar='type=TYPE[,cookie_name=COOKIE_NAME]',
            type=utils.str2dict_type(required_keys=['type'],
                                     optional_keys=['cookie_name']),
            help=_('The type of session persistence to use and associated '
                   'cookie name.'))
        session_group.add_argument(
            '--no-session-persistence',
            action='store_true',
            help=_('Clear session persistence for the pool.'))
        _add_common_args(parser, False)

    def args2body(self, parsed_args):
        body = _parse_common_args(parsed_args)
        if parsed_args.no_session_persistence:
            body['session_persistence'] = None
        elif parsed_args.session_persistence:
            body['session_persistence'] = parsed_args.session_persistence
        neutronV20.update_dict(parsed_args, body,
                               ['admin_state_up'])
        return {self.resource: body}


class DeletePool(neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given pool."""

    resource = 'pool'
    shadow_resource = 'lbaas_pool'
