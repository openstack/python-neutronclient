# Copyright 2013 OpenStack LLC.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging

from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.neutron.v2_0 import network
from neutronclient.neutron.v2_0 import router
from neutronclient.openstack.common.gettextutils import _
PERFECT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class AddNetworkToDhcpAgent(neutronV20.NeutronCommand):
    """Add a network to a DHCP agent."""

    log = logging.getLogger(__name__ + '.AddNetworkToDhcpAgent')

    def get_parser(self, prog_name):
        parser = super(AddNetworkToDhcpAgent, self).get_parser(prog_name)
        parser.add_argument(
            'dhcp_agent',
            help='ID of the DHCP agent')
        parser.add_argument(
            'network',
            help='network to add')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _net_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'network', parsed_args.network)
        neutron_client.add_network_to_dhcp_agent(parsed_args.dhcp_agent,
                                                 {'network_id': _net_id})
        print >>self.app.stdout, (
            _('Added network %s to DHCP agent') % parsed_args.network)


class RemoveNetworkFromDhcpAgent(neutronV20.NeutronCommand):
    """Remove a network from a DHCP agent."""
    log = logging.getLogger(__name__ + '.RemoveNetworkFromDhcpAgent')

    def get_parser(self, prog_name):
        parser = super(RemoveNetworkFromDhcpAgent, self).get_parser(prog_name)
        parser.add_argument(
            'dhcp_agent',
            help='ID of the DHCP agent')
        parser.add_argument(
            'network',
            help='network to remove')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _net_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'network', parsed_args.network)
        neutron_client.remove_network_from_dhcp_agent(
            parsed_args.dhcp_agent, _net_id)
        print >>self.app.stdout, (
            _('Removed network %s to DHCP agent') % parsed_args.network)


class ListNetworksOnDhcpAgent(network.ListNetwork):
    """List the networks on a DHCP agent."""

    log = logging.getLogger(__name__ + '.ListNetworksOnDhcpAgent')
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListNetworksOnDhcpAgent,
                       self).get_parser(prog_name)
        parser.add_argument(
            'dhcp_agent',
            help='ID of the DHCP agent')
        return parser

    def call_server(self, neutron_client, search_opts, parsed_args):
        data = neutron_client.list_networks_on_dhcp_agent(
            parsed_args.dhcp_agent, **search_opts)
        return data


class ListDhcpAgentsHostingNetwork(neutronV20.ListCommand):
    """List DHCP agents hosting a network."""

    resource = 'agent'
    _formatters = {}
    log = logging.getLogger(__name__ + '.ListDhcpAgentsHostingNetwork')
    list_columns = ['id', 'host', 'admin_state_up', 'alive']
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListDhcpAgentsHostingNetwork,
                       self).get_parser(prog_name)
        parser.add_argument(
            'network',
            help='network to query')
        return parser

    def extend_list(self, data, parsed_args):
        for agent in data:
            agent['alive'] = ":-)" if agent['alive'] else 'xxx'

    def call_server(self, neutron_client, search_opts, parsed_args):
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       'network',
                                                       parsed_args.network)
        search_opts['network'] = _id
        data = neutron_client.list_dhcp_agent_hosting_networks(**search_opts)
        return data


class AddRouterToL3Agent(neutronV20.NeutronCommand):
    """Add a router to a L3 agent."""

    log = logging.getLogger(__name__ + '.AddRouterToL3Agent')

    def get_parser(self, prog_name):
        parser = super(AddRouterToL3Agent, self).get_parser(prog_name)
        parser.add_argument(
            'l3_agent',
            help='ID of the L3 agent')
        parser.add_argument(
            'router',
            help='router to add')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'router', parsed_args.router)
        neutron_client.add_router_to_l3_agent(parsed_args.l3_agent,
                                              {'router_id': _id})
        print >>self.app.stdout, (
            _('Added router %s to L3 agent') % parsed_args.router)


class RemoveRouterFromL3Agent(neutronV20.NeutronCommand):
    """Remove a router from a L3 agent."""

    log = logging.getLogger(__name__ + '.RemoveRouterFromL3Agent')

    def get_parser(self, prog_name):
        parser = super(RemoveRouterFromL3Agent, self).get_parser(prog_name)
        parser.add_argument(
            'l3_agent',
            help='ID of the L3 agent')
        parser.add_argument(
            'router',
            help='router to remove')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'router', parsed_args.router)
        neutron_client.remove_router_from_l3_agent(
            parsed_args.l3_agent, _id)
        print >>self.app.stdout, (
            _('Removed Router %s to L3 agent') % parsed_args.router)


class ListRoutersOnL3Agent(neutronV20.ListCommand):
    """List the routers on a L3 agent."""

    log = logging.getLogger(__name__ + '.ListRoutersOnL3Agent')
    _formatters = {'external_gateway_info':
                   router._format_external_gateway_info}
    list_columns = ['id', 'name', 'external_gateway_info']
    resource = 'router'
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListRoutersOnL3Agent,
                       self).get_parser(prog_name)
        parser.add_argument(
            'l3_agent',
            help='ID of the L3 agent to query')
        return parser

    def call_server(self, neutron_client, search_opts, parsed_args):
        data = neutron_client.list_routers_on_l3_agent(
            parsed_args.l3_agent, **search_opts)
        return data


class ListL3AgentsHostingRouter(neutronV20.ListCommand):
    """List L3 agents hosting a router."""

    resource = 'agent'
    _formatters = {}
    log = logging.getLogger(__name__ + '.ListL3AgentsHostingRouter')
    list_columns = ['id', 'host', 'admin_state_up', 'alive']
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListL3AgentsHostingRouter,
                       self).get_parser(prog_name)
        parser.add_argument('router',
                            help='router to query')
        return parser

    def extend_list(self, data, parsed_args):
        for agent in data:
            agent['alive'] = ":-)" if agent['alive'] else 'xxx'

    def call_server(self, neutron_client, search_opts, parsed_args):
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       'router',
                                                       parsed_args.router)
        search_opts['router'] = _id
        data = neutron_client.list_l3_agent_hosting_routers(**search_opts)
        return data


class ListPoolsOnLbaasAgent(neutronV20.ListCommand):
    """List the pools on a loadbalancer agent."""

    log = logging.getLogger(__name__ + '.ListPoolsOnLbaasAgent')
    list_columns = ['id', 'name', 'lb_method', 'protocol',
                    'admin_state_up', 'status']
    resource = 'pool'
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(ListPoolsOnLbaasAgent, self).get_parser(prog_name)
        parser.add_argument(
            'lbaas_agent',
            help='ID of the loadbalancer agent to query')
        return parser

    def call_server(self, neutron_client, search_opts, parsed_args):
        data = neutron_client.list_pools_on_lbaas_agent(
            parsed_args.lbaas_agent, **search_opts)
        return data


class GetLbaasAgentHostingPool(neutronV20.ListCommand):
    """Get loadbalancer agent hosting a pool.

    Deriving from ListCommand though server will return only one agent
    to keep common output format for all agent schedulers
    """

    resource = 'agent'
    log = logging.getLogger(__name__ + '.GetLbaasAgentHostingPool')
    list_columns = ['id', 'host', 'admin_state_up', 'alive']
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super(GetLbaasAgentHostingPool,
                       self).get_parser(prog_name)
        parser.add_argument('pool',
                            help='pool to query')
        return parser

    def extend_list(self, data, parsed_args):
        for agent in data:
            agent['alive'] = ":-)" if agent['alive'] else 'xxx'

    def call_server(self, neutron_client, search_opts, parsed_args):
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       'pool',
                                                       parsed_args.pool)
        search_opts['pool'] = _id
        agent = neutron_client.get_lbaas_agent_hosting_pool(**search_opts)
        data = {'agents': [agent['agent']]}
        return data
