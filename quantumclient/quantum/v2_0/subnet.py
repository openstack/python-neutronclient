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

from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient.quantum import v2_0 as quantumv20
from quantumclient.quantum.v2_0 import CreateCommand
from quantumclient.quantum.v2_0 import DeleteCommand
from quantumclient.quantum.v2_0 import ListCommand
from quantumclient.quantum.v2_0 import ShowCommand
from quantumclient.quantum.v2_0 import UpdateCommand


def _format_allocation_pools(subnet):
    try:
        return '\n'.join([utils.dumps(pool) for pool in
                          subnet['allocation_pools']])
    except Exception:
        return ''


def _format_dns_nameservers(subnet):
    try:
        return '\n'.join([utils.dumps(server) for server in
                          subnet['dns_nameservers']])
    except Exception:
        return ''


def _format_host_routes(subnet):
    try:
        return '\n'.join([utils.dumps(route) for route in
                          subnet['host_routes']])
    except Exception:
        return ''


class ListSubnet(ListCommand):
    """List networks that belong to a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ListSubnet')
    _formatters = {'allocation_pools': _format_allocation_pools,
                   'dns_nameservers': _format_dns_nameservers,
                   'host_routes': _format_host_routes, }
    list_columns = ['id', 'name', 'cidr', 'allocation_pools']


class ShowSubnet(ShowCommand):
    """Show information of a given subnet."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ShowSubnet')


class CreateSubnet(CreateCommand):
    """Create a subnet for a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.CreateSubnet')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help='name of this subnet')
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4, choices=[4, 6],
            help='IP version with default 4')
        parser.add_argument(
            '--ip_version',
            type=int,
            choices=[4, 6],
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--gateway', metavar='gateway',
            help='gateway ip of this subnet')
        parser.add_argument(
            '--no-gateway',
            default=False, action='store_true',
            help='No distribution of gateway')
        parser.add_argument(
            '--allocation-pool',
            action='append',
            help='Allocation pool IP addresses for this subnet: '
            'start=<ip_address>,end=<ip_address> '
            'can be repeated')
        parser.add_argument(
            '--allocation_pool',
            action='append',
            help=argparse.SUPPRESS)
        parser.add_argument(
            'network_id', metavar='network',
            help='Network id or name this subnet belongs to')
        parser.add_argument(
            'cidr', metavar='cidr',
            help='cidr of subnet to create')

    def args2body(self, parsed_args):
        _network_id = quantumv20.find_resourceid_by_name_or_id(
            self.get_client(), 'network', parsed_args.network_id)
        body = {'subnet': {'cidr': parsed_args.cidr,
                           'network_id': _network_id,
                           'ip_version': parsed_args.ip_version, }, }

        if parsed_args.gateway and parsed_args.no_gateway:
            raise exceptions.CommandError("--gateway option and "
                                          "--no-gateway option can "
                                          "not be used same time")
        if parsed_args.no_gateway:
            body['subnet'].update({'gateway_ip': None})
        if parsed_args.gateway:
            body['subnet'].update({'gateway_ip': parsed_args.gateway})
        if parsed_args.tenant_id:
            body['subnet'].update({'tenant_id': parsed_args.tenant_id})
        if parsed_args.name:
            body['subnet'].update({'name': parsed_args.name})
        ips = []
        if parsed_args.allocation_pool:
            for ip_spec in parsed_args.allocation_pool:
                ips.append(utils.str2dict(ip_spec))
        if ips:
            body['subnet'].update({'allocation_pools': ips})

        return body


class DeleteSubnet(DeleteCommand):
    """Delete a given subnet."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.DeleteSubnet')


class UpdateSubnet(UpdateCommand):
    """Update subnet's information."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.UpdateSubnet')
