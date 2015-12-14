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
from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20


def add_common_args(parser):
    parser.add_argument(
        '--name',
        help=_('Name for the firewall.'))
    parser.add_argument(
        '--description',
        help=_('Description for the firewall.'))
    router = parser.add_mutually_exclusive_group()
    router.add_argument(
        '--router',
        dest='routers',
        metavar='ROUTER',
        action='append',
        help=_('ID or name of the router associated with the firewall '
               '(requires FWaaS router insertion extension to be enabled). '
               'This option can be repeated.'))
    router.add_argument(
        '--no-routers',
        action='store_true',
        help=_('Associate no routers with the firewall (requires FWaaS '
               'router insertion extension).'))


def parse_common_args(client, parsed_args):
    body = {}
    if parsed_args.policy:
        body['firewall_policy_id'] = neutronv20.find_resourceid_by_name_or_id(
            client, 'firewall_policy',
            parsed_args.policy)

    if parsed_args.routers:
        body['router_ids'] = [
            neutronv20.find_resourceid_by_name_or_id(client, 'router', r)
            for r in parsed_args.routers]
    elif parsed_args.no_routers:
        body['router_ids'] = []

    neutronv20.update_dict(parsed_args, body,
                           ['name', 'description'])
    return body


class ListFirewall(neutronv20.ListCommand):
    """List firewalls that belong to a given tenant."""

    resource = 'firewall'
    list_columns = ['id', 'name', 'firewall_policy_id']
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowFirewall(neutronv20.ShowCommand):
    """Show information of a given firewall."""

    resource = 'firewall'


class CreateFirewall(neutronv20.CreateCommand):
    """Create a firewall."""

    resource = 'firewall'

    def add_known_arguments(self, parser):
        add_common_args(parser)
        parser.add_argument(
            'policy', metavar='POLICY',
            help=_('ID or name of the firewall policy '
                   'associated to this firewall.'))
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state',
            action='store_false',
            help=_('Set admin state up to false.'))

    def args2body(self, parsed_args):
        body = parse_common_args(self.get_client(), parsed_args)
        neutronv20.update_dict(parsed_args, body, ['tenant_id'])
        body['admin_state_up'] = parsed_args.admin_state
        return {self.resource: body}


class UpdateFirewall(neutronv20.UpdateCommand):
    """Update a given firewall."""

    resource = 'firewall'

    def add_known_arguments(self, parser):
        add_common_args(parser)
        parser.add_argument(
            '--policy', metavar='POLICY',
            help=_('ID or name of the firewall policy '
                   'associated to this firewall.'))
        utils.add_boolean_argument(
            parser, '--admin-state-up', dest='admin_state_up',
            help=_('Update the admin state for the firewall '
                   '(True means UP).'))

    def args2body(self, parsed_args):
        body = parse_common_args(self.get_client(), parsed_args)
        neutronv20.update_dict(parsed_args, body, ['admin_state_up'])
        return {self.resource: body}


class DeleteFirewall(neutronv20.DeleteCommand):
    """Delete a given firewall."""

    resource = 'firewall'
