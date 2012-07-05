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

import logging

from quantumclient.quantum.v2_0 import CreateCommand
from quantumclient.quantum.v2_0 import DeleteCommand
from quantumclient.quantum.v2_0 import ListCommand
from quantumclient.quantum.v2_0 import ShowCommand
from quantumclient.quantum.v2_0 import UpdateCommand


class ListSubnet(ListCommand):
    """List networks that belong to a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ListSubnet')
    _formatters = {}


class ShowSubnet(ShowCommand):
    """Show information of a given subnet."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.ShowSubnet')


class CreateSubnet(CreateCommand):
    """Create a subnet for a given tenant."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.CreateSubnet')

    def add_known_arguments(self, parser):
        parser.add_argument('--ip_version', type=int,
                            default=4, choices=[4, 6],
                            help='IP version with default 4')
        parser.add_argument(
            '--gateway', metavar='gateway',
            help='gateway ip of this subnet')
        parser.add_argument(
            'network_id',
            help='Network id of this subnet belongs to')
        parser.add_argument(
            'cidr', metavar='cidr',
            help='cidr of subnet to create')

    def args2body(self, parsed_args):
        body = {'subnet': {'cidr': parsed_args.cidr,
                           'network_id': parsed_args.network_id,
                           'ip_version': parsed_args.ip_version, }, }
        if parsed_args.gateway:
            body['subnet'].update({'gateway_ip': parsed_args.gateway})
        if parsed_args.tenant_id:
            body['subnet'].update({'tenant_id': parsed_args.tenant_id})
        return body


class DeleteSubnet(DeleteCommand):
    """Delete a given subnet."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.DeleteSubnet')


class UpdateSubnet(UpdateCommand):
    """Update subnet's information."""

    resource = 'subnet'
    log = logging.getLogger(__name__ + '.UpdateSubnet')
