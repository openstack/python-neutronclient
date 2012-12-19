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


class ListPool(quantumv20.ListCommand):
    """List pools that belong to a given tenant."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.ListPool')
    list_columns = ['id', 'name', 'lb_method', 'protocol',
                    'admin_state_up', 'status']
    _formatters = {}


class ShowPool(quantumv20.ShowCommand):
    """Show information of a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.ShowPool')


class CreatePool(quantumv20.CreateCommand):
    """Create a pool"""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.CreatePool')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='set admin state up to false')
        parser.add_argument(
            '--description',
            help='description of the pool')
        parser.add_argument(
            '--lb-method',
            required=True,
            help='the algorithm used to distribute load between the members '
                 'of the pool')
        parser.add_argument(
            '--name',
            required=True,
            help='the name of the pool')
        parser.add_argument(
            '--protocol',
            required=True,
            help='protocol for balancing')
        parser.add_argument(
            '--subnet-id',
            required=True,
            help='the subnet on which the members of the pool will be located')

    def args2body(self, parsed_args):
        body = {
            self.resource: {
                'admin_state_up': parsed_args.admin_state_down,
            },
        }
        quantumv20.update_dict(parsed_args, body[self.resource],
                               ['description', 'lb_method', 'name',
                                'subnet_id', 'protocol', 'tenant_id'])
        return body


class UpdatePool(quantumv20.UpdateCommand):
    """Update a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.UpdatePool')


class DeletePool(quantumv20.DeleteCommand):
    """Delete a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.DeletePool')


class RetrievePoolStats(quantumv20.ShowCommand):
    """Retrieve stats for a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.RetrievePoolStats')

    def get_data(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        params = {}
        if parsed_args.fields:
            params = {'fields': parsed_args.fields}

        data = quantum_client.retrieve_pool_stats(parsed_args.id, **params)
        self.format_output_data(data)
        stats = data['stats']
        if 'stats' in data:
            return zip(*sorted(stats.iteritems()))
        else:
            return None
