# Copyright 2013 OpenStack Foundation.
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

from neutronclient.neutron import v2_0 as neutronV20


def _format_timestamp(component):
    try:
        return component['heartbeat_timestamp'].split(".", 2)[0]
    except Exception:
        return ''


class ListAgent(neutronV20.ListCommand):
    """List agents."""

    resource = 'agent'
    log = logging.getLogger(__name__ + '.ListAgent')
    list_columns = ['id', 'agent_type', 'host', 'alive', 'admin_state_up']
    _formatters = {'heartbeat_timestamp': _format_timestamp}

    def extend_list(self, data, parsed_args):
        for agent in data:
            agent['alive'] = ":-)" if agent['alive'] else 'xxx'


class ShowAgent(neutronV20.ShowCommand):
    """Show information of a given agent."""

    resource = 'agent'
    log = logging.getLogger(__name__ + '.ShowAgent')
    allow_names = False
    json_indent = 5


class DeleteAgent(neutronV20.DeleteCommand):
    """Delete a given agent."""

    log = logging.getLogger(__name__ + '.DeleteAgent')
    resource = 'agent'
    allow_names = False


class UpdateAgent(neutronV20.UpdateCommand):
    """Update a given agent."""

    log = logging.getLogger(__name__ + '.UpdateAgent')
    resource = 'agent'
    allow_names = False
