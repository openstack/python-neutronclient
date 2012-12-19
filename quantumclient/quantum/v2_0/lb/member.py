# Copyright 2013 Mirantis Inc.
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
# @author: Ilya Shakhat, Mirantis Inc.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging

from quantumclient.quantum import v2_0 as quantumv20


class ListMember(quantumv20.ListCommand):
    """List members that belong to a given tenant."""

    resource = 'member'
    log = logging.getLogger(__name__ + '.ListMember')
    list_columns = ['id', 'address', 'port', 'admin_state_up', 'status']
    _formatters = {}


class ShowMember(quantumv20.ShowCommand):
    """Show information of a given member."""

    resource = 'member'
    log = logging.getLogger(__name__ + '.ShowMember')


class CreateMember(quantumv20.CreateCommand):
    """Create a member"""

    resource = 'member'
    log = logging.getLogger(__name__ + '.CreateMember')

    def add_known_arguments(self, parser):
        parser.add_argument(
            'pool_id', metavar='pool',
            help='Pool id or name this vip belongs to')
        parser.add_argument(
            '--address',
            required=True,
            help='IP address of the pool member on the pool network. ')
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='set admin state up to false')
        parser.add_argument(
            '--port',
            required=True,
            help='port on which the pool member listens for requests or '
                 'connections. ')
        parser.add_argument(
            '--weight',
            help='weight of pool member in the pool')

    def args2body(self, parsed_args):
        _pool_id = quantumv20.find_resourceid_by_name_or_id(
            self.get_client(), 'pool', parsed_args.pool_id)
        body = {
            self.resource: {
                'pool_id': _pool_id,
                'admin_state_up': parsed_args.admin_state_down,
            },
        }
        quantumv20.update_dict(parsed_args, body[self.resource],
                               ['address', 'port', 'weight', 'tenant_id'])
        return body


class UpdateMember(quantumv20.UpdateCommand):
    """Update a given member."""

    resource = 'member'
    log = logging.getLogger(__name__ + '.UpdateMember')


class DeleteMember(quantumv20.DeleteCommand):
    """Delete a given member."""

    resource = 'member'
    log = logging.getLogger(__name__ + '.DeleteMember')
