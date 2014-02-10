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

from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _

RESOURCE = 'network_gateway'


class ListNetworkGateway(neutronV20.ListCommand):
    """List network gateways for a given tenant."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.ListNetworkGateway')
    list_columns = ['id', 'name']


class ShowNetworkGateway(neutronV20.ShowCommand):
    """Show information of a given network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.ShowNetworkGateway')


class CreateNetworkGateway(neutronV20.CreateCommand):
    """Create a network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.CreateNetworkGateway')

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of network gateway to create'))
        parser.add_argument(
            '--device',
            action='append',
            help=_('Device info for this gateway '
            'device_id=<device identifier>,'
            'interface_name=<name_or_identifier> '
            'It can be repeated for multiple devices for HA gateways'))

    def args2body(self, parsed_args):
        body = {self.resource: {
            'name': parsed_args.name}}
        devices = []
        if parsed_args.device:
            for device in parsed_args.device:
                devices.append(utils.str2dict(device))
        if devices:
            body[self.resource].update({'devices': devices})
        if parsed_args.tenant_id:
            body[self.resource].update({'tenant_id': parsed_args.tenant_id})
        return body


class DeleteNetworkGateway(neutronV20.DeleteCommand):
    """Delete a given network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.DeleteNetworkGateway')


class UpdateNetworkGateway(neutronV20.UpdateCommand):
    """Update the name for a network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.UpdateNetworkGateway')


class NetworkGatewayInterfaceCommand(neutronV20.NeutronCommand):
    """Base class for connecting/disconnecting networks to/from a gateway."""

    resource = RESOURCE

    def get_parser(self, prog_name):
        parser = super(NetworkGatewayInterfaceCommand,
                       self).get_parser(prog_name)
        parser.add_argument(
            'net_gateway_id', metavar='NET-GATEWAY-ID',
            help=_('ID of the network gateway'))
        parser.add_argument(
            'network_id', metavar='NETWORK-ID',
            help=_('ID of the internal network to connect on the gateway'))
        parser.add_argument(
            '--segmentation-type',
            help=_('L2 segmentation strategy on the external side of '
                   'the gateway (e.g.: VLAN, FLAT)'))
        parser.add_argument(
            '--segmentation-id',
            help=_('Identifier for the L2 segment on the external side '
                   'of the gateway'))
        return parser

    def retrieve_ids(self, client, args):
        gateway_id = neutronV20.find_resourceid_by_name_or_id(
            client, self.resource, args.net_gateway_id)
        network_id = neutronV20.find_resourceid_by_name_or_id(
            client, 'network', args.network_id)
        return (gateway_id, network_id)


class ConnectNetworkGateway(NetworkGatewayInterfaceCommand):
    """Add an internal network interface to a router."""

    log = logging.getLogger(__name__ + '.ConnectNetworkGateway')

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        (gateway_id, network_id) = self.retrieve_ids(neutron_client,
                                                     parsed_args)
        neutron_client.connect_network_gateway(
            gateway_id, {'network_id': network_id,
                         'segmentation_type': parsed_args.segmentation_type,
                         'segmentation_id': parsed_args.segmentation_id})
        # TODO(Salvatore-Orlando): Do output formatting as
        # any other command
        print >>self.app.stdout, (
            _('Connected network to gateway %s') % gateway_id)


class DisconnectNetworkGateway(NetworkGatewayInterfaceCommand):
    """Remove a network from a network gateway."""

    log = logging.getLogger(__name__ + '.DisconnectNetworkGateway')

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        (gateway_id, network_id) = self.retrieve_ids(neutron_client,
                                                     parsed_args)
        neutron_client.disconnect_network_gateway(
            gateway_id, {'network_id': network_id,
                         'segmentation_type': parsed_args.segmentation_type,
                         'segmentation_id': parsed_args.segmentation_id})
        # TODO(Salvatore-Orlando): Do output formatting as
        # any other command
        print >>self.app.stdout, (
            _('Disconnected network from gateway %s') % gateway_id)
