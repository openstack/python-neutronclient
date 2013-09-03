# Copyright 2012 OpenStack LLC.
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

import argparse
import logging

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


def _format_external_gateway_info(router):
    try:
        return utils.dumps(router['external_gateway_info'])
    except Exception:
        return ''


class ListRouter(neutronV20.ListCommand):
    """List routers that belong to a given tenant."""

    resource = 'router'
    log = logging.getLogger(__name__ + '.ListRouter')
    _formatters = {'external_gateway_info': _format_external_gateway_info, }
    list_columns = ['id', 'name', 'external_gateway_info']
    pagination_support = True
    sorting_support = True


class ShowRouter(neutronV20.ShowCommand):
    """Show information of a given router."""

    resource = 'router'
    log = logging.getLogger(__name__ + '.ShowRouter')


class CreateRouter(neutronV20.CreateCommand):
    """Create a router for a given tenant."""

    resource = 'router'
    log = logging.getLogger(__name__ + '.CreateRouter')
    _formatters = {'external_gateway_info': _format_external_gateway_info, }

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help='Set Admin State Up to false')
        parser.add_argument(
            '--admin_state_down',
            dest='admin_state', action='store_false',
            help=argparse.SUPPRESS)
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of router to create')
        parser.add_argument(
            'distributed', action='store_true',
            help='Create a distributed router (Nicira plugin only)')

    def args2body(self, parsed_args):
        body = {'router': {
            'name': parsed_args.name,
            'admin_state_up': parsed_args.admin_state, }, }
        if parsed_args.tenant_id:
            body['router'].update({'tenant_id': parsed_args.tenant_id})
        return body


class DeleteRouter(neutronV20.DeleteCommand):
    """Delete a given router."""

    log = logging.getLogger(__name__ + '.DeleteRouter')
    resource = 'router'


class UpdateRouter(neutronV20.UpdateCommand):
    """Update router's information."""

    log = logging.getLogger(__name__ + '.UpdateRouter')
    resource = 'router'


class RouterInterfaceCommand(neutronV20.NeutronCommand):
    """Based class to Add/Remove router interface."""

    api = 'network'
    resource = 'router'

    def call_api(self, neutron_client, router_id, body):
        raise NotImplementedError()

    def success_message(self, router_id, portinfo):
        raise NotImplementedError()

    def get_parser(self, prog_name):
        parser = super(RouterInterfaceCommand, self).get_parser(prog_name)
        parser.add_argument(
            'router_id', metavar='router-id',
            help='ID of the router')
        parser.add_argument(
            'interface', metavar='INTERFACE',
            help='The format is "SUBNET|subnet=SUBNET|port=PORT". '
            'Either a subnet or port must be specified. '
            'Both ID and name are accepted as SUBNET or PORT. '
            'Note that "subnet=" can be omitted when specifying subnet.')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format

        if '=' in parsed_args.interface:
            resource, value = parsed_args.interface.split('=', 1)
            if resource not in ['subnet', 'port']:
                exceptions.CommandError('You must specify either subnet or '
                                        'port for INTERFACE parameter.')
        else:
            resource = 'subnet'
            value = parsed_args.interface

        _router_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, self.resource, parsed_args.router_id)

        _interface_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, resource, value)
        body = {'%s_id' % resource: _interface_id}

        portinfo = self.call_api(neutron_client, _router_id, body)
        print >>self.app.stdout, self.success_message(parsed_args.router_id,
                                                      portinfo)


class AddInterfaceRouter(RouterInterfaceCommand):
    """Add an internal network interface to a router."""

    log = logging.getLogger(__name__ + '.AddInterfaceRouter')

    def call_api(self, neutron_client, router_id, body):
        return neutron_client.add_interface_router(router_id, body)

    def success_message(self, router_id, portinfo):
        return (_('Added interface %(port)s to router %(router)s.') %
                {'router': router_id, 'port': portinfo['port_id']})


class RemoveInterfaceRouter(RouterInterfaceCommand):
    """Remove an internal network interface from a router."""

    log = logging.getLogger(__name__ + '.RemoveInterfaceRouter')

    def call_api(self, neutron_client, router_id, body):
        return neutron_client.remove_interface_router(router_id, body)

    def success_message(self, router_id, portinfo):
        # portinfo is not used since it is None for router-interface-delete.
        return _('Removed interface from router %s.') % router_id


class SetGatewayRouter(neutronV20.NeutronCommand):
    """Set the external network gateway for a router."""

    log = logging.getLogger(__name__ + '.SetGatewayRouter')
    api = 'network'
    resource = 'router'

    def get_parser(self, prog_name):
        parser = super(SetGatewayRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router_id', metavar='router-id',
            help='ID of the router')
        parser.add_argument(
            'external_network_id', metavar='external-network-id',
            help='ID of the external network for the gateway')
        parser.add_argument(
            '--disable-snat', action='store_true',
            help='Disable Source NAT on the router gateway')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _router_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, self.resource, parsed_args.router_id)
        _ext_net_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'network', parsed_args.external_network_id)
        router_dict = {'network_id': _ext_net_id}
        if parsed_args.disable_snat:
            router_dict['enable_snat'] = False
        neutron_client.add_gateway_router(_router_id, router_dict)
        print >>self.app.stdout, (
            _('Set gateway for router %s') % parsed_args.router_id)


class RemoveGatewayRouter(neutronV20.NeutronCommand):
    """Remove an external network gateway from a router."""

    log = logging.getLogger(__name__ + '.RemoveGatewayRouter')
    api = 'network'
    resource = 'router'

    def get_parser(self, prog_name):
        parser = super(RemoveGatewayRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router_id', metavar='router-id',
            help='ID of the router')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _router_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, self.resource, parsed_args.router_id)
        neutron_client.remove_gateway_router(_router_id)
        print >>self.app.stdout, (
            _('Removed gateway from router %s') % parsed_args.router_id)
