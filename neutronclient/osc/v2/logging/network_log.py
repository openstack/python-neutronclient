# Copyright 2017-2018 FUJTISU LIMITED.
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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util
from oslo_log import log as logging

from neutronclient._i18n import _
from neutronclient.common import utils as nc_utils
from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.fwaas import constants as fwaas_const

LOG = logging.getLogger(__name__)

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('enabled', 'Enabled', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('target_id', 'Target', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('resource_id', 'Resource', column_util.LIST_LONG_ONLY),
    ('resource_type', 'Type', column_util.LIST_BOTH),
    ('event', 'Event', column_util.LIST_LONG_ONLY),
    ('summary', 'Summary', column_util.LIST_SHORT_ONLY),
)

_attr_map_for_loggable = (
    ('type', 'Supported types', column_util.LIST_BOTH),
)

NET_LOG = 'network_log'


def _get_common_parser(parser):
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_('Description of the network log'))
    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument(
        '--enable',
        action='store_true',
        help=_('Enable this log (default is disabled)'))
    enable_group.add_argument(
        '--disable',
        action='store_true',
        help=_('Disable this log'))
    return parser


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    client = client_manager.neutronclient

    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['project_id'] = osc_utils.find_project(
                client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
        resource_type = parsed_args.resource_type
        attrs['resource_type'] = resource_type
        if parsed_args.resource:
            cmd_resource = None
            if resource_type == fwaas_const.FWG:
                cmd_resource = fwaas_const.CMD_FWG
            attrs['resource_id'] = client.find_resource(
                resource_type,
                parsed_args.resource,
                cmd_resource=cmd_resource)['id']

        if parsed_args.target:
            # NOTE(yushiro) Currently, we're supporting only port
            attrs['target_id'] = client.find_resource(
                'port', parsed_args.target)['id']
        if parsed_args.event:
            attrs['event'] = parsed_args.event
    if parsed_args.enable:
        attrs['enabled'] = True
    if parsed_args.disable:
        attrs['enabled'] = False
    if parsed_args.name:
        attrs['name'] = parsed_args.name
    if parsed_args.description:
        attrs['description'] = parsed_args.description
    return attrs


class CreateNetworkLog(command.ShowOne):
    _description = _("Create a new network log")

    def get_parser(self, prog_name):
        parser = super(CreateNetworkLog, self).get_parser(prog_name)
        _get_common_parser(parser)
        osc_utils.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name for the network log'))
        parser.add_argument(
            '--event',
            metavar='{ALL,ACCEPT,DROP}',
            choices=['ALL', 'ACCEPT', 'DROP'],
            type=nc_utils.convert_to_uppercase,
            help=_('An event to store with log'))
        # NOTE(yushiro) '--resource-type' is managed by following command:
        # "openstack network loggable resources list". Therefore, this option
        # shouldn't have "choices" like ['security_group', 'firewall_group']
        parser.add_argument(
            '--resource-type',
            metavar='<resource-type>',
            required=True,
            type=nc_utils.convert_to_lowercase,
            help=_('Network log type(s). '
                   'You can see supported type(s) with following command:\n'
                   '$ openstack network loggable resources list'))
        parser.add_argument(
            '--resource',
            metavar='<resource>',
            help=_('Name or ID of resource (security group or firewall group) '
                   'that used for logging. You can control for logging target '
                   'combination with --target option.'))
        parser.add_argument(
            '--target',
            metavar='<target>',
            help=_('Port (name or ID) for logging. You can control '
                   'for logging target combination with --resource option.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        obj = client.create_network_log({'log': attrs})['log']
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)


class DeleteNetworkLog(command.Command):
    _description = _("Delete network log(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteNetworkLog, self).get_parser(prog_name)
        parser.add_argument(
            'network_log',
            metavar='<network-log>',
            nargs='+',
            help=_('Network log(s) to delete (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        result = 0
        for log_res in parsed_args.network_log:
            try:
                log_id = client.find_resource(
                    'log', log_res, cmd_resource=NET_LOG)['id']
                client.delete_network_log(log_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete network log with "
                            "name or ID '%(network_log)s': %(e)s"),
                          {'network_log': log_res, 'e': e})

        if result > 0:
            total = len(parsed_args.network_log)
            msg = (_("%(result)s of %(total)s network log(s) "
                     "failed to delete") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListLoggableResource(command.Lister):
    _description = _("List supported loggable resources")

    def get_parser(self, prog_name):
        parser = super(ListLoggableResource, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        obj = client.list_network_loggable_resources()['loggable_resources']
        headers, columns = column_util.get_column_definitions(
            _attr_map_for_loggable, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(s, columns) for s in obj))


class ListNetworkLog(command.Lister):
    _description = _("List network logs")

    def get_parser(self, prog_name):
        parser = super(ListNetworkLog, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        # TODO(yushiro): We'll support filtering in the future.
        return parser

    def _extend_list(self, data, parsed_args):
        ext_data = copy.deepcopy(data)
        for d in ext_data:
            e_prefix = 'Event: '
            if d['event']:
                event = e_prefix + d['event'].upper()
            port = '(port) ' + d['target_id'] if d['target_id'] else ''
            resource_type = d['resource_type']
            if d['resource_id']:
                res = '(%s) %s' % (resource_type, d['resource_id'])
            else:
                res = ''
            t_prefix = 'Logged: '
            if port and res:
                t = '%s on %s' % (res, port)
            else:
                # Either of res and port is empty, so concatenation works fine
                t = res + port
            target = t_prefix + t if t else t_prefix + '(None specified)'
            d['summary'] = ',\n'.join([event, target])
        return ext_data

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        obj = client.list_network_logs()['logs']
        obj_extend = self._extend_list(obj, parsed_args)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (
            utils.get_dict_properties(s, columns) for s in obj_extend))


class SetNetworkLog(command.Command):
    _description = _("Set network log properties")

    def get_parser(self, prog_name):
        parser = super(SetNetworkLog, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            'network_log',
            metavar='<network-log>',
            help=_('Network log to set (name or ID)'))
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the network log'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        log_id = client.find_resource(
            'log', parsed_args.network_log, cmd_resource=NET_LOG)['id']
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        try:
            client.update_network_log(log_id, {'log': attrs})
        except Exception as e:
            msg = (_("Failed to set network log '%(logging)s': %(e)s")
                   % {'logging': parsed_args.network_log, 'e': e})
            raise exceptions.CommandError(msg)


class ShowNetworkLog(command.ShowOne):
    _description = _("Display network log details")

    def get_parser(self, prog_name):
        parser = super(ShowNetworkLog, self).get_parser(prog_name)
        parser.add_argument(
            'network_log',
            metavar='<network-log>',
            help=_('Network log to show (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        log_id = client.find_resource(
            'log', parsed_args.network_log, cmd_resource=NET_LOG)['id']
        obj = client.show_network_log(log_id)['log']
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)
