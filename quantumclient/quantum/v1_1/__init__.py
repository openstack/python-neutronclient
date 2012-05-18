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

from quantumclient.common import command
from quantumclient.common import utils


class QuantumCommand(command.OpenStackCommand):
    api = 'network'
    log = logging.getLogger(__name__ + '.QuantumCommand')

    def get_parser(self, prog_name):
        parser = super(QuantumCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--request-format',
            help=_('the xml or json request format'),
            default='json',
            choices=['json', 'xml', ], )
        parser.add_argument(
            'tenant_id', metavar='tenant-id',
            help=_('the owner tenant ID'), )
        return parser


class QuantumPortCommand(QuantumCommand):
    api = 'network'
    log = logging.getLogger(__name__ + '.QuantumPortCommand')

    def get_parser(self, prog_name):
        parser = super(QuantumPortCommand, self).get_parser(prog_name)
        parser.add_argument(
            'net_id', metavar='net-id',
            help=_('the owner network ID'), )
        return parser


class QuantumInterfaceCommand(QuantumPortCommand):
    api = 'network'
    log = logging.getLogger(__name__ + '.QuantumInterfaceCommand')

    def get_parser(self, prog_name):
        parser = super(QuantumInterfaceCommand, self).get_parser(prog_name)
        parser.add_argument(
            'port_id', metavar='port-id',
            help=_('the owner Port ID'), )
        return parser
