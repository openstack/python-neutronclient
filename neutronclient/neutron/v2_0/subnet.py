# Copyright 2012 OpenStack Foundation.
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

import argparse
import logging

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


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


class ListSubnet(neutronV20.ListCommand):
    """List subnets that belong to a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ListSubnet')
    _formatters = {'allocation_pools': _format_allocation_pools,
                   'dns_nameservers': _format_dns_nameservers,
                   'host_routes': _format_host_routes, }
    list_columns = ['id', 'name', 'cidr', 'allocation_pools']
    pagination_support = True
    sorting_support = True


class ShowSubnet(neutronV20.ShowCommand):
    """Show information of a given subnet."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ShowSubnet')


class CreateSubnet(neutronV20.CreateCommand):
    """Create a subnet for a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.CreateSubnet')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Name of this subnet'))
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4, choices=[4, 6],
            help=_('IP version with default 4'))
        parser.add_argument(
            '--ip_version',
            type=int,
            choices=[4, 6],
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--gateway', metavar='GATEWAY_IP',
            help=_('Gateway ip of this subnet'))
        parser.add_argument(
            '--no-gateway',
            action='store_true',
            help=_('No distribution of gateway'))
        parser.add_argument(
            '--allocation-pool', metavar='start=IP_ADDR,end=IP_ADDR',
            action='append', dest='allocation_pools', type=utils.str2dict,
            help=_('Allocation pool IP addresses for this subnet '
            '(This option can be repeated)'))
        parser.add_argument(
            '--allocation_pool',
            action='append', dest='allocation_pools', type=utils.str2dict,
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--host-route', metavar='destination=CIDR,nexthop=IP_ADDR',
            action='append', dest='host_routes', type=utils.str2dict,
            help=_('Additional route (This option can be repeated)'))
        parser.add_argument(
            '--dns-nameserver', metavar='DNS_NAMESERVER',
            action='append', dest='dns_nameservers',
            help=_('DNS name server for this subnet '
            '(This option can be repeated)'))
        parser.add_argument(
            '--disable-dhcp',
            action='store_true',
            help=_('Disable DHCP for this subnet'))
        parser.add_argument(
            'network_id', metavar='NETWORK',
            help=_('Network id or name this subnet belongs to'))
        parser.add_argument(
            'cidr', metavar='CIDR',
            help=_('CIDR of subnet to create'))

    def args2body(self, parsed_args):
        _network_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'network', parsed_args.network_id)
        body = {'subnet': {'cidr': parsed_args.cidr,
                           'network_id': _network_id,
                           'ip_version': parsed_args.ip_version, }, }

        if parsed_args.gateway and parsed_args.no_gateway:
            raise exceptions.CommandError(_("--gateway option and "
                                          "--no-gateway option can "
                                          "not be used same time"))
        if parsed_args.no_gateway:
            body['subnet'].update({'gateway_ip': None})
        if parsed_args.gateway:
            body['subnet'].update({'gateway_ip': parsed_args.gateway})
        if parsed_args.tenant_id:
            body['subnet'].update({'tenant_id': parsed_args.tenant_id})
        if parsed_args.name:
            body['subnet'].update({'name': parsed_args.name})
        if parsed_args.disable_dhcp:
            body['subnet'].update({'enable_dhcp': False})
        if parsed_args.allocation_pools:
            body['subnet']['allocation_pools'] = parsed_args.allocation_pools
        if parsed_args.host_routes:
            body['subnet']['host_routes'] = parsed_args.host_routes
        if parsed_args.dns_nameservers:
            body['subnet']['dns_nameservers'] = parsed_args.dns_nameservers

        return body


class DeleteSubnet(neutronV20.DeleteCommand):
    """Delete a given subnet."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.DeleteSubnet')


class UpdateSubnet(neutronV20.UpdateCommand):
    """Update subnet's information."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.UpdateSubnet')
