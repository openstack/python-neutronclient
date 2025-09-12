# All Rights Reserved 2020
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

import logging

from osc_lib.cli import format_columns
from osc_lib.cli import identity as identity_utils
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.osc.v2.taas import tap_service

LOG = logging.getLogger(__name__)

TAP_FLOW = 'tap_flow'
TAP_FLOWS = '%ss' % TAP_FLOW

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('tenant_id', 'Tenant', column_util.LIST_LONG_ONLY),
    ('name', 'Name', column_util.LIST_BOTH),
    ('status', 'Status', column_util.LIST_BOTH),
    ('source_port', 'source_port', column_util.LIST_BOTH),
    ('tap_service_id', 'tap_service_id', column_util.LIST_BOTH),
    ('direction', 'Direction', column_util.LIST_BOTH),
)

_formatters = {
    'vlan_filter': format_columns.ListColumn,
}


def _add_updatable_args(parser):
    parser.add_argument(
        '--name',
        help=_('Name of this Tap service.'))
    parser.add_argument(
        '--description',
        help=_('Description for this Tap service.'))


class CreateTapFlow(command.ShowOne):
    _description = _("Create a tap flow")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        identity_utils.add_project_owner_option_to_parser(parser)
        _add_updatable_args(parser)
        parser.add_argument(
            '--port',
            required=True,
            metavar="SOURCE_PORT",
            help=_('Source port to which the Tap Flow is connected.'))
        parser.add_argument(
            '--tap-service',
            required=True,
            metavar="TAP_SERVICE",
            help=_('Tap Service to which the Tap Flow belongs.'))
        parser.add_argument(
            '--direction',
            required=True,
            metavar="DIRECTION",
            choices=['IN', 'OUT', 'BOTH'],
            type=lambda s: s.upper(),
            help=_('Direction of the Tap flow. Possible options are: '
                   'IN, OUT, BOTH'))
        parser.add_argument(
            '--vlan-filter',
            required=False,
            metavar="VLAN_FILTER",
            help=_('VLAN Ids to be mirrored in the form of range string.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            attrs['description'] = str(parsed_args.description)
        if parsed_args.port is not None:
            source_port = client.find_port(parsed_args.port)['id']
            attrs['source_port'] = source_port
        if parsed_args.tap_service is not None:
            tap_service_id = client.find_tap_service(
                parsed_args.tap_service)['id']
            attrs['tap_service_id'] = tap_service_id
        if parsed_args.direction is not None:
            attrs['direction'] = parsed_args.direction
        if parsed_args.vlan_filter is not None:
            attrs['vlan_filter'] = parsed_args.vlan_filter
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = identity_utils.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id
        obj = client.create_tap_flow(**attrs)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class ListTapFlow(command.Lister):
    _description = _("List tap flows that belong to a given tenant")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        identity_utils.add_project_owner_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        params = {}
        if parsed_args.project is not None:
            project_id = identity_utils.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            params['tenant_id'] = project_id
        objs = client.tap_flows(retrieve_all=True, params=params)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=True)
        return (headers, (osc_utils.get_dict_properties(
            s, columns, formatters=_formatters) for s in objs))


class ShowTapFlow(command.ShowOne):
    _description = _("Show information of a given tap flow")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_FLOW,
            metavar="<%s>" % TAP_FLOW,
            help=_("ID or name of tap flow to look up."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_tap_flow(parsed_args.tap_flow,
                                  ignore_missing=False).id
        obj = client.get_tap_flow(id)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteTapFlow(command.Command):
    _description = _("Delete a tap flow")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_FLOW,
            metavar="<%s>" % TAP_FLOW,
            nargs="+",
            help=_("ID(s) or name(s) of tap flow to delete."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fails = 0
        for id_or_name in parsed_args.tap_flow:
            try:
                id = client.find_tap_flow(id_or_name,
                                          ignore_missing=False).id
                client.delete_tap_flow(id)
                LOG.warning("Tap flow %(id)s deleted", {'id': id})
            except Exception as e:
                fails += 1
                LOG.error("Failed to delete tap flow with name or ID "
                          "'%(id_or_name)s': %(e)s",
                          {'id_or_name': id_or_name, 'e': e})
        if fails > 0:
            msg = (_("Failed to delete %(fails)s of %(total)s tap flow.") %
                   {'fails': fails, 'total': len(parsed_args.tap_flow)})
            raise exceptions.CommandError(msg)


class UpdateTapFlow(command.ShowOne):
    _description = _("Update a tap flow.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_FLOW,
            metavar="<%s>" % TAP_FLOW,
            help=_("ID or name of tap flow to update."),
        )
        _add_updatable_args(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        original_t_f = client.find_tap_flow(parsed_args.tap_flow,
                                            ignore_missing=False).id
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            attrs['description'] = str(parsed_args.description)
        obj = client.update_tap_flow(original_t_f, **attrs)
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data
