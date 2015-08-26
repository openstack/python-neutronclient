# Copyright 2016 Radware LTD.
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


def _get_listener_id(client, listener_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(
        client, 'listener', listener_id_or_name)


def _get_pool_id(client, pool_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(
        client, 'pool', pool_id_or_name, cmd_resource='lbaas_pool')


def _add_common_args(parser, is_create=True):
    parser.add_argument(
        '--name',
        help=_('Name of the policy.'))
    parser.add_argument(
        '--description',
        help=_('Description of the policy.'))
    parser.add_argument(
        '--action',
        required=is_create,
        metavar='ACTION',
        type=utils.convert_to_uppercase,
        choices=['REJECT', 'REDIRECT_TO_POOL', 'REDIRECT_TO_URL'],
        help=_('Action type of the policy.'))
    parser.add_argument(
        '--redirect-pool',
        help=_('ID or name of the pool for REDIRECT_TO_POOL action type.'))
    parser.add_argument(
        '--redirect-url',
        help=_('URL for REDIRECT_TO_URL action type. '
               'This should be a valid URL string.'))
    parser.add_argument(
        '--position',
        type=int,
        help=_('L7 policy position in ordered policies list. '
               'This must be an integer starting from 1. '
               'Not specifying the position will place the policy '
               'at the tail of existing policies list.'))


def _common_args2body(client, parsed_args, is_create=True):
    if parsed_args.redirect_url:
        if parsed_args.action != 'REDIRECT_TO_URL':
            raise exceptions.CommandError(_('Action must be REDIRECT_TO_URL'))
    if parsed_args.redirect_pool:
        if parsed_args.action != 'REDIRECT_TO_POOL':
            raise exceptions.CommandError(_('Action must be REDIRECT_TO_POOL'))
        parsed_args.redirect_pool_id = _get_pool_id(
            client, parsed_args.redirect_pool)
    if (parsed_args.action == 'REDIRECT_TO_URL' and
            not parsed_args.redirect_url):
        raise exceptions.CommandError(_('Redirect URL must be specified'))
    if (parsed_args.action == 'REDIRECT_TO_POOL' and
            not parsed_args.redirect_pool):
        raise exceptions.CommandError(_('Redirect pool must be specified'))

    attributes = ['name', 'description',
                  'action', 'redirect_pool_id', 'redirect_url',
                  'position', 'admin_state_up']
    if is_create:
        parsed_args.listener_id = _get_listener_id(
            client, parsed_args.listener)
        attributes.extend(['listener_id', 'tenant_id'])
    body = {}
    neutronV20.update_dict(parsed_args, body, attributes)
    return {'l7policy': body}


class ListL7Policy(neutronV20.ListCommand):
    """LBaaS v2 List L7 policies that belong to a given listener."""

    resource = 'l7policy'
    shadow_resource = 'lbaas_l7policy'
    pagination_support = True
    sorting_support = True
    list_columns = [
        'id', 'name', 'action', 'redirect_pool_id', 'redirect_url',
        'position', 'admin_state_up', 'status'
    ]


class ShowL7Policy(neutronV20.ShowCommand):
    """LBaaS v2 Show information of a given L7 policy."""

    resource = 'l7policy'
    shadow_resource = 'lbaas_l7policy'


class CreateL7Policy(neutronV20.CreateCommand):
    """LBaaS v2 Create L7 policy."""

    resource = 'l7policy'
    shadow_resource = 'lbaas_l7policy'

    def add_known_arguments(self, parser):
        _add_common_args(parser)
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state_up',
            action='store_false',
            help=_('Set admin state up to false.'))
        parser.add_argument(
            '--listener',
            required=True,
            metavar='LISTENER',
            help=_('ID or name of the listener this policy belongs to.'))

    def args2body(self, parsed_args):
        return _common_args2body(self.get_client(), parsed_args)


class UpdateL7Policy(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given L7 policy."""

    resource = 'l7policy'
    shadow_resource = 'lbaas_l7policy'

    def add_known_arguments(self, parser):
        _add_common_args(parser, is_create=False)
        utils.add_boolean_argument(
            parser, '--admin-state-up',
            help=_('Specify the administrative state of the policy'
                   ' (True meaning "Up").'))

    def args2body(self, parsed_args):
        return _common_args2body(self.get_client(), parsed_args, False)


class DeleteL7Policy(neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given L7 policy."""

    resource = 'l7policy'
    shadow_resource = 'lbaas_l7policy'
