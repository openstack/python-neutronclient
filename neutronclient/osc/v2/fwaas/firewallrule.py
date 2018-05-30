# Copyright 2016-2017 FUJITSU LIMITED
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
import copy
import logging

from cliff import columns as cliff_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.common import utils as nc_utils
from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.fwaas import constants as const


LOG = logging.getLogger(__name__)


_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('enabled', 'Enabled', column_util.LIST_BOTH),
    ('summary', 'Summary', column_util.LIST_SHORT_ONLY),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('ip_version', 'IP Version', column_util.LIST_LONG_ONLY),
    ('action', 'Action', column_util.LIST_LONG_ONLY),
    ('protocol', 'Protocol', column_util.LIST_LONG_ONLY),
    ('source_ip_address', 'Source IP Address', column_util.LIST_LONG_ONLY),
    ('source_port', 'Source Port', column_util.LIST_LONG_ONLY),
    ('destination_ip_address', 'Destination IP Address',
        column_util.LIST_LONG_ONLY),
    ('destination_port', 'Destination Port', column_util.LIST_LONG_ONLY),
    ('shared', 'Shared', column_util.LIST_LONG_ONLY),
    ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
    ('source_firewall_group_id', 'Source Firewall Group ID',
     column_util.LIST_LONG_ONLY),
    ('destination_firewall_group_id', 'Destination Firewall Group ID',
     column_util.LIST_LONG_ONLY),
)


def _get_common_parser(parser):
    parser.add_argument(
        '--name',
        metavar='<name>',
        help=_('Name of the firewall rule'))
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_('Description of the firewall rule'))
    parser.add_argument(
        '--protocol',
        choices=['tcp', 'udp', 'icmp', 'any'],
        type=nc_utils.convert_to_lowercase,
        help=_('Protocol for the firewall rule'))
    parser.add_argument(
        '--action',
        choices=['allow', 'deny', 'reject'],
        type=nc_utils.convert_to_lowercase,
        help=_('Action for the firewall rule'))
    parser.add_argument(
        '--ip-version',
        metavar='<ip-version>',
        choices=['4', '6'],
        help=_('Set IP version 4 or 6 (default is 4)'))
    src_ip_group = parser.add_mutually_exclusive_group()
    src_ip_group.add_argument(
        '--source-ip-address',
        metavar='<source-ip-address>',
        help=_('Source IP address or subnet'))
    src_ip_group.add_argument(
        '--no-source-ip-address',
        action='store_true',
        help=_('Detach source IP address'))
    dst_ip_group = parser.add_mutually_exclusive_group()
    dst_ip_group.add_argument(
        '--destination-ip-address',
        metavar='<destination-ip-address>',
        help=_('Destination IP address or subnet'))
    dst_ip_group.add_argument(
        '--no-destination-ip-address',
        action='store_true',
        help=_('Detach destination IP address'))
    src_port_group = parser.add_mutually_exclusive_group()
    src_port_group.add_argument(
        '--source-port',
        metavar='<source-port>',
        help=_('Source port number or range'
               '(integer in [1, 65535] or range like 123:456)'))
    src_port_group.add_argument(
        '--no-source-port',
        action='store_true',
        help=_('Detach source port number or range'))
    dst_port_group = parser.add_mutually_exclusive_group()
    dst_port_group.add_argument(
        '--destination-port',
        metavar='<destination-port>',
        help=_('Destination port number or range'
               '(integer in [1, 65535] or range like 123:456)'))
    dst_port_group.add_argument(
        '--no-destination-port',
        action='store_true',
        help=_('Detach destination port number or range'))
    shared_group = parser.add_mutually_exclusive_group()
    shared_group.add_argument(
        '--public',
        action='store_true',
        help=_('Make the firewall policy public, which allows it to be '
               'used in all projects (as opposed to the default, '
               'which is to restrict its use to the current project). '
               'This option is deprecated and would be removed in R Release'))
    shared_group.add_argument(
        '--private',
        action='store_true',
        help=_(
            'Restrict use of the firewall rule to the current project.'
            'This option is deprecated and would be removed in R release.'))
    shared_group.add_argument(
        '--share',
        action='store_true',
        help=_('Share the firewall rule to be used in all projects '
               '(by default, it is restricted to be used by the '
               'current project).'))
    shared_group.add_argument(
        '--no-share',
        action='store_true',
        help=_('Restrict use of the firewall rule to the current project'))
    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        '--enable-rule',
        action='store_true',
        help=_('Enable this rule (default is enabled)'))
    enable_group.add_argument(
        '--disable-rule',
        action='store_true',
        help=_('Disable this rule'))
    src_fwg_group = parser.add_mutually_exclusive_group()
    src_fwg_group.add_argument(
        '--source-firewall-group',
        metavar='<source-firewall-group>',
        help=_('Source firewall group (name or ID)'))
    src_fwg_group.add_argument(
        '--no-source-firewall-group',
        action='store_true',
        help=_('No associated destination firewall group'))
    dst_fwg_group = parser.add_mutually_exclusive_group()
    dst_fwg_group.add_argument(
        '--destination-firewall-group',
        metavar='<destination-firewall-group>',
        help=_('Destination firewall group (name or ID)'))
    dst_fwg_group.add_argument(
        '--no-destination-firewall-group',
        action='store_true',
        help=_('No associated destination firewall group'))
    return parser


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    client = client_manager.neutronclient
    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['tenant_id'] = osc_utils.find_project(
                client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
    if parsed_args.name:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.description:
        attrs['description'] = str(parsed_args.description)
    if parsed_args.protocol:
        protocol = parsed_args.protocol
        attrs['protocol'] = None if protocol == 'any' else protocol
    if parsed_args.action:
        attrs['action'] = parsed_args.action
    if parsed_args.ip_version:
        attrs['ip_version'] = str(parsed_args.ip_version)
    if parsed_args.source_port:
        attrs['source_port'] = parsed_args.source_port
    if parsed_args.no_source_port:
        attrs['source_port'] = None
    if parsed_args.source_ip_address:
        attrs['source_ip_address'] = parsed_args.source_ip_address
    if parsed_args.no_source_ip_address:
        attrs['source_ip_address'] = None
    if parsed_args.destination_port:
        attrs['destination_port'] = str(parsed_args.destination_port)
    if parsed_args.no_destination_port:
        attrs['destination_port'] = None
    if parsed_args.destination_ip_address:
        attrs['destination_ip_address'] = str(
            parsed_args.destination_ip_address)
    if parsed_args.no_destination_ip_address:
        attrs['destination_ip_address'] = None
    if parsed_args.enable_rule:
        attrs['enabled'] = True
    if parsed_args.disable_rule:
        attrs['enabled'] = False
    if parsed_args.share or parsed_args.public:
        attrs['shared'] = True
    if parsed_args.no_share or parsed_args.private:
        attrs['shared'] = False
    if parsed_args.source_firewall_group:
        attrs['source_firewall_group_id'] = client.find_resource(
            const.FWG, parsed_args.source_firewall_group,
            cmd_resource=const.CMD_FWG)['id']
    if parsed_args.no_source_firewall_group:
        attrs['source_firewall_group_id'] = None
    if parsed_args.destination_firewall_group:
        attrs['destination_firewall_group_id'] = client.find_resource(
            const.FWG, parsed_args.destination_firewall_group,
            cmd_resource=const.CMD_FWG)['id']
    if parsed_args.no_destination_firewall_group:
        attrs['destination_firewall_group_id'] = None
    return attrs


class ProtocolColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return self._value if self._value else 'any'


_formatters = {'protocol': ProtocolColumn}


class CreateFirewallRule(command.ShowOne):
    _description = _("Create a new firewall rule")

    def get_parser(self, prog_name):
        parser = super(CreateFirewallRule, self).get_parser(prog_name)
        _get_common_parser(parser)
        osc_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        obj = client.create_fwaas_firewall_rule(
            {const.FWR: attrs})[const.FWR]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns, formatters=_formatters)
        return display_columns, data


class DeleteFirewallRule(command.Command):
    _description = _("Delete firewall rule(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteFirewallRule, self).get_parser(prog_name)
        parser.add_argument(
            const.FWR,
            metavar='<firewall-rule>',
            nargs='+',
            help=_('Firewall rule(s) to delete (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        result = 0
        for fwr in parsed_args.firewall_rule:
            try:
                fwr_id = client.find_resource(
                    const.FWR, fwr, cmd_resource=const.CMD_FWR)['id']
                client.delete_fwaas_firewall_rule(fwr_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete Firewall rule with "
                            "name or ID '%(firewall_rule)s': %(e)s"),
                          {const.FWR: fwr, 'e': e})

        if result > 0:
            total = len(parsed_args.firewall_rule)
            msg = (_("%(result)s of %(total)s firewall rule(s) failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListFirewallRule(command.Lister):
    _description = _("List firewall rules that belong to a given tenant")

    def get_parser(self, prog_name):
        parser = super(ListFirewallRule, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def extend_list(self, data, parsed_args):
        ext_data = copy.deepcopy(data)
        for d in ext_data:
            protocol = d['protocol'].upper() if d['protocol'] else 'ANY'
            src_ip = 'none specified'
            dst_ip = 'none specified'
            src_port = '(none specified)'
            dst_port = '(none specified)'
            if 'source_ip_address' in d and d['source_ip_address']:
                src_ip = str(d['source_ip_address']).lower()
            if 'source_port' in d and d['source_port']:
                src_port = '(' + str(d['source_port']).lower() + ')'
            if 'destination_ip_address' in d and d['destination_ip_address']:
                dst_ip = str(d['destination_ip_address']).lower()
            if 'destination_port' in d and d['destination_port']:
                dst_port = '(' + str(d['destination_port']).lower() + ')'
            action = d['action'] if d.get('action') else 'no-action'
            src = 'source(port): ' + src_ip + src_port
            dst = 'dest(port): ' + dst_ip + dst_port
            d['summary'] = ',\n '.join([protocol, src, dst, action])
        return ext_data

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        obj = client.list_fwaas_firewall_rules()[const.FWRS]
        obj_extend = self.extend_list(obj, parsed_args)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(
            s, columns, formatters=_formatters) for s in obj_extend))


class SetFirewallRule(command.Command):
    _description = _("Set firewall rule properties")

    def get_parser(self, prog_name):
        parser = super(SetFirewallRule, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            const.FWR,
            metavar='<firewall-rule>',
            help=_('Firewall rule to set (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager,
                                  parsed_args, is_create=False)
        fwr_id = client.find_resource(
            const.FWR, parsed_args.firewall_rule,
            cmd_resource=const.CMD_FWR)['id']
        try:
            client.update_fwaas_firewall_rule(fwr_id, {const.FWR: attrs})
        except Exception as e:
            msg = (_("Failed to set firewall rule '%(rule)s': %(e)s")
                   % {'rule': parsed_args.firewall_rule, 'e': e})
            raise exceptions.CommandError(msg)


class ShowFirewallRule(command.ShowOne):
    _description = _("Display firewall rule details")

    def get_parser(self, prog_name):
        parser = super(ShowFirewallRule, self).get_parser(prog_name)
        parser.add_argument(
            const.FWR,
            metavar='<firewall-rule>',
            help=_('Firewall rule to display (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        fwr_id = client.find_resource(
            const.FWR, parsed_args.firewall_rule,
            cmd_resource=const.CMD_FWR)['id']
        obj = client.show_fwaas_firewall_rule(fwr_id)[const.FWR]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


class UnsetFirewallRule(command.Command):
    _description = _("Unset firewall rule properties")

    def get_parser(self, prog_name):
        parser = super(UnsetFirewallRule, self).get_parser(prog_name)
        parser.add_argument(
            const.FWR,
            metavar='<firewall-rule>',
            help=_('Firewall rule to unset (name or ID)'))
        parser.add_argument(
            '--source-ip-address',
            action='store_true',
            help=_('Source IP address or subnet'))
        parser.add_argument(
            '--destination-ip-address',
            action='store_true',
            help=_('Destination IP address or subnet'))
        parser.add_argument(
            '--source-port',
            action='store_true',
            help=_('Source port number or range'
                   '(integer in [1, 65535] or range like 123:456)'))
        parser.add_argument(
            '--destination-port',
            action='store_true',
            help=_('Destination port number or range'
                   '(integer in [1, 65535] or range like 123:456)'))
        parser.add_argument(
            '--share',
            action='store_true',
            help=_('Restrict use of the firewall rule to the current project'))
        parser.add_argument(
            '--public',
            action='store_true',
            help=_('Restrict use of the firewall rule to the current project. '
                   'This option is deprecated and would be removed in '
                   'R Release.'))
        parser.add_argument(
            '--enable-rule',
            action='store_true',
            help=_('Disable this rule'))

        parser.add_argument(
            '--source-firewall-group',
            action='store_true',
            help=_('Source firewall group (name or ID)'))

        parser.add_argument(
            '--destination-firewall-group',
            action='store_true',
            help=_('Destination firewall group (name or ID)'))
        return parser

    def _get_attrs(self, client_manager, parsed_args):
        attrs = {}
        if parsed_args.source_ip_address:
            attrs['source_ip_address'] = None
        if parsed_args.source_port:
            attrs['source_port'] = None
        if parsed_args.destination_ip_address:
            attrs['destination_ip_address'] = None
        if parsed_args.destination_port:
            attrs['destination_port'] = None
        if parsed_args.share or parsed_args.public:
            attrs['shared'] = False
        if parsed_args.enable_rule:
            attrs['enabled'] = False
        if parsed_args.source_firewall_group:
            attrs['source_firewall_group_id'] = None
        if parsed_args.source_firewall_group:
            attrs['destination_firewall_group_id'] = None
        return attrs

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = self._get_attrs(self.app.client_manager, parsed_args)
        fwr_id = client.find_resource(
            const.FWR, parsed_args.firewall_rule,
            cmd_resource=const.CMD_FWR)['id']
        try:
            client.update_fwaas_firewall_rule(fwr_id, {const.FWR: attrs})
        except Exception as e:
            msg = (_("Failed to unset firewall rule '%(rule)s': %(e)s")
                   % {'rule': parsed_args.firewall_rule, 'e': e})
            raise exceptions.CommandError(msg)
