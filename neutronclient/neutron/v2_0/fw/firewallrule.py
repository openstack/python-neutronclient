# Copyright 2013 Big Switch Networks
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

from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20


def _add_common_args(parser, is_create=True):
    """If is_create is True, protocol and action become mandatory arguments.

    CreateCommand = is_create : True
    UpdateCommand = is_create : False
    """
    parser.add_argument(
        '--name',
        help=_('Name for the firewall rule.'))
    parser.add_argument(
        '--description',
        help=_('Description for the firewall rule.'))
    parser.add_argument(
        '--source-ip-address',
        help=_('Source IP address or subnet.'))
    parser.add_argument(
        '--destination-ip-address',
        help=_('Destination IP address or subnet.'))
    parser.add_argument(
        '--source-port',
        help=_('Source port (integer in [1, 65535] or range in a:b).'))
    parser.add_argument(
        '--destination-port',
        help=_('Destination port (integer in [1, 65535] or range in '
               'a:b).'))
    utils.add_boolean_argument(
        parser, '--enabled', dest='enabled',
        help=_('Whether to enable or disable this rule.'))
    parser.add_argument(
        '--protocol', choices=['tcp', 'udp', 'icmp', 'any'],
        required=is_create,
        type=utils.convert_to_lowercase,
        help=_('Protocol for the firewall rule.'))
    parser.add_argument(
        '--action',
        required=is_create,
        type=utils.convert_to_lowercase,
        choices=['allow', 'deny', 'reject'],
        help=_('Action for the firewall rule.'))


def common_args2body(parsed_args):
    body = {}
    neutronv20.update_dict(parsed_args, body,
                           ['name', 'description', 'shared', 'tenant_id',
                            'source_ip_address', 'destination_ip_address',
                            'source_port', 'destination_port', 'action',
                            'enabled', 'ip_version'])
    protocol = parsed_args.protocol
    if protocol:
        if protocol == 'any':
            protocol = None
        body['protocol'] = protocol
    return body


class ListFirewallRule(neutronv20.ListCommand):
    """List firewall rules that belong to a given tenant."""

    resource = 'firewall_rule'
    list_columns = ['id', 'name', 'firewall_policy_id', 'summary', 'enabled']
    pagination_support = True
    sorting_support = True

    def extend_list(self, data, parsed_args):
        for d in data:
            val = []
            if d.get('protocol'):
                protocol = d['protocol'].upper()
            else:
                protocol = 'no-protocol'
            val.append(protocol)
            if 'source_ip_address' in d and 'source_port' in d:
                src = 'source: ' + str(d['source_ip_address']).lower()
                src = src + '(' + str(d['source_port']).lower() + ')'
            else:
                src = 'source: none specified'
            val.append(src)
            if 'destination_ip_address' in d and 'destination_port' in d:
                dst = 'dest: ' + str(d['destination_ip_address']).lower()
                dst = dst + '(' + str(d['destination_port']).lower() + ')'
            else:
                dst = 'dest: none specified'
            val.append(dst)
            if 'action' in d:
                action = d['action']
            else:
                action = 'no-action'
            val.append(action)
            d['summary'] = ',\n '.join(val)


class ShowFirewallRule(neutronv20.ShowCommand):
    """Show information of a given firewall rule."""

    resource = 'firewall_rule'


class CreateFirewallRule(neutronv20.CreateCommand):
    """Create a firewall rule."""

    resource = 'firewall_rule'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--shared',
            action='store_true',
            help=_('Set shared flag for the firewall rule.'),
            default=argparse.SUPPRESS)
        _add_common_args(parser)
        parser.add_argument(
            '--ip-version',
            type=int, choices=[4, 6], default=4,
            help=_('IP version for the firewall rule (default is 4).'))

    def args2body(self, parsed_args):
        return {self.resource: common_args2body(parsed_args)}


class UpdateFirewallRule(neutronv20.UpdateCommand):
    """Update a given firewall rule."""

    resource = 'firewall_rule'

    def add_known_arguments(self, parser):
        utils.add_boolean_argument(
            parser,
            '--shared',
            dest='shared',
            help=_('Update the shared flag for the firewall rule.'),
            default=argparse.SUPPRESS)
        parser.add_argument(
            '--ip-version',
            type=int, choices=[4, 6],
            help=_('Update IP version for the firewall rule.'))
        _add_common_args(parser, is_create=False)

    def args2body(self, parsed_args):
        return {self.resource: common_args2body(parsed_args)}


class DeleteFirewallRule(neutronv20.DeleteCommand):
    """Delete a given firewall rule."""

    resource = 'firewall_rule'
