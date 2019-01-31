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
from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


def _get_pool_id(client, pool_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(client, 'pool',
                                                    pool_id_or_name,
                                                    cmd_resource='lbaas_pool')


class LbaasMemberMixin(object):

    def set_extra_attrs(self, parsed_args):
        self.parent_id = _get_pool_id(self.get_client(), parsed_args.pool)

    def add_known_arguments(self, parser):
        parser.add_argument(
            'pool', metavar='POOL',
            help=_('ID or name of the pool that this member belongs to.'))


def _add_common_args(parser):
    parser.add_argument(
        '--name',
        help=_('Name of the member.'))
    parser.add_argument(
        '--weight',
        help=_('Weight of the member in the pool (default:1, [0..256]).'))


def _parse_common_args(body, parsed_args):
    neutronV20.update_dict(parsed_args, body, ['weight', 'name'])


class ListMember(LbaasMemberMixin, neutronV20.ListCommand):
    """LBaaS v2 List members that belong to a given pool."""

    resource = 'member'
    shadow_resource = 'lbaas_member'
    list_columns = [
        'id', 'name', 'address', 'protocol_port', 'weight',
        'subnet_id', 'admin_state_up', 'status'
    ]
    pagination_support = True
    sorting_support = True

    def take_action(self, parsed_args):
        self.parent_id = _get_pool_id(self.get_client(), parsed_args.pool)
        self.values_specs.append('--pool_id=%s' % self.parent_id)
        return super(ListMember, self).take_action(parsed_args)


class ShowMember(LbaasMemberMixin, neutronV20.ShowCommand):
    """LBaaS v2 Show information of a given member."""

    resource = 'member'
    shadow_resource = 'lbaas_member'


class CreateMember(neutronV20.CreateCommand):
    """LBaaS v2 Create a member."""

    resource = 'member'
    shadow_resource = 'lbaas_member'

    def add_known_arguments(self, parser):
        _add_common_args(parser)
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false.'))
        parser.add_argument(
            '--subnet',
            required=True,
            help=_('Subnet ID or name for the member.'))
        parser.add_argument(
            '--address',
            required=True,
            help=_('IP address of the pool member in the pool.'))
        parser.add_argument(
            '--protocol-port',
            required=True,
            help=_('Port on which the pool member listens for requests or '
                   'connections.'))
        parser.add_argument(
            'pool', metavar='POOL',
            help=_('ID or name of the pool that this member belongs to.'))

    def args2body(self, parsed_args):
        self.parent_id = _get_pool_id(self.get_client(), parsed_args.pool)
        _subnet_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'subnet', parsed_args.subnet)
        body = {'subnet_id': _subnet_id,
                'admin_state_up': parsed_args.admin_state,
                'protocol_port': parsed_args.protocol_port,
                'address': parsed_args.address}
        neutronV20.update_dict(parsed_args, body,
                               ['subnet_id', 'tenant_id'])
        _parse_common_args(body, parsed_args)
        return {self.resource: body}


class UpdateMember(neutronV20.UpdateCommand):
    """LBaaS v2 Update a given member."""

    resource = 'member'
    shadow_resource = 'lbaas_member'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'pool', metavar='POOL',
            help=_('ID or name of the pool that this member belongs to.'))
        utils.add_boolean_argument(
            parser, '--admin-state-up',
            help=_('Update the administrative state of '
                   'the member (True meaning "Up").'))
        _add_common_args(parser)

    def args2body(self, parsed_args):
        self.parent_id = _get_pool_id(self.get_client(), parsed_args.pool)
        body = {}
        if hasattr(parsed_args, "admin_state_up"):
            body['admin_state_up'] = parsed_args.admin_state_up
        _parse_common_args(body, parsed_args)
        return {self.resource: body}


class DeleteMember(LbaasMemberMixin, neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given member."""

    resource = 'member'
    shadow_resource = 'lbaas_member'
