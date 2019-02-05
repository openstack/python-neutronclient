# Copyright (c) 2019 SUSE Linux Products GmbH
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

"""Subnet onboard action implementation"""
import logging

from osc_lib.command import command
from osc_lib import exceptions

from neutronclient._i18n import _

LOG = logging.getLogger(__name__)


class NetworkOnboardSubnets(command.Command):
    """Onboard network subnets into a subnet pool"""

    def get_parser(self, prog_name):
        parser = super(NetworkOnboardSubnets, self).get_parser(prog_name)
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Onboard all subnets associated with this network")
        )
        parser.add_argument(
            'subnetpool',
            metavar="<subnetpool>",
            help=_("Target subnet pool for onboarding subnets")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        subnetpool_id = _get_id(client, parsed_args.subnetpool, 'subnetpool')
        network_id = _get_id(client, parsed_args.network, 'network')
        body = {'network_id': network_id}
        try:
            client.onboard_network_subnets(subnetpool_id, body)
        except Exception as e:
            msg = (_("Failed to onboard subnets for network '%(n)s': %(e)s")
                   % {'n': parsed_args.network, 'e': e})
            raise exceptions.CommandError(msg)


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, str(id_or_name))['id']
