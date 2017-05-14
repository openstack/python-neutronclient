# Copyright 2016 ZTE Corporation.
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

"""Network trunk and subports action implementations"""
import logging

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils

from neutronclient._i18n import _
from neutronclient.osc import utils as nc_osc_utils
from neutronclient.osc.v2 import utils as v2_utils

LOG = logging.getLogger(__name__)

TRUNK = 'trunk'
TRUNKS = 'trunks'
SUB_PORTS = 'sub_ports'


class CreateNetworkTrunk(command.ShowOne):
    """Create a network trunk for a given project"""

    def get_parser(self, prog_name):
        parser = super(CreateNetworkTrunk, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("Name of the trunk to create")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("A description of the trunk")
        )
        parser.add_argument(
            '--parent-port',
            metavar='<parent-port>',
            required=True,
            help=_("Parent port belonging to this trunk (name or ID)")
        )
        parser.add_argument(
            '--subport',
            metavar='<port=,segmentation-type=,segmentation-id=>',
            action=parseractions.MultiKeyValueAction, dest='add_subports',
            optional_keys=['segmentation-id', 'segmentation-type'],
            required_keys=['port'],
            help=_("Subport to add. Subport is of form "
                   "\'port=<name or ID>,segmentation-type=,segmentation-ID=\' "
                   "(--subport) option can be repeated")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable trunk (default)")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable trunk")
        )
        nc_osc_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_attrs_for_trunk(self.app.client_manager,
                                     parsed_args)
        body = {TRUNK: attrs}
        obj = client.create_trunk(body)
        columns = _get_columns(obj[TRUNK])
        data = osc_utils.get_dict_properties(obj[TRUNK], columns,
                                             formatters=_formatters)
        return columns, data


class DeleteNetworkTrunk(command.Command):
    """Delete a given network trunk"""

    def get_parser(self, prog_name):
        parser = super(DeleteNetworkTrunk, self).get_parser(prog_name)
        parser.add_argument(
            'trunk',
            metavar="<trunk>",
            nargs="+",
            help=_("Trunk(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        result = 0
        for trunk in parsed_args.trunk:
            try:
                trunk_id = _get_id(client, trunk, TRUNK)
                client.delete_trunk(trunk_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete trunk with name "
                          "or ID '%(trunk)s': %(e)s"),
                          {'trunk': trunk, 'e': e})
        if result > 0:
            total = len(parsed_args.trunk)
            msg = (_("%(result)s of %(total)s trunks failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListNetworkTrunk(command.Lister):
    """List all network trunks"""

    def get_parser(self, prog_name):
        parser = super(ListNetworkTrunk, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        data = client.list_trunks()
        headers = (
            'ID',
            'Name',
            'Parent Port',
            'Description'
        )
        columns = (
            'id',
            'name',
            'port_id',
            'description'
        )
        if parsed_args.long:
            headers += (
                'Status',
                'State',
                'Created At',
                'Updated At',
            )
            columns += (
                'status',
                'admin_state_up',
                'created_at',
                'updated_at'
            )
        return (headers,
                (osc_utils.get_dict_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data[TRUNKS]))


class SetNetworkTrunk(command.Command):
    """Set network trunk properties"""

    def get_parser(self, prog_name):
        parser = super(SetNetworkTrunk, self).get_parser(prog_name)
        parser.add_argument(
            'trunk',
            metavar="<trunk>",
            help=_("Trunk to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help=_("Set trunk name")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("A description of the trunk")
        )
        parser.add_argument(
            '--subport',
            metavar='<port=,segmentation-type=,segmentation-id=>',
            action=parseractions.MultiKeyValueAction, dest='set_subports',
            optional_keys=['segmentation-id', 'segmentation-type'],
            required_keys=['port'],
            help=_("Subport to add. Subport is of form "
                   "\'port=<name or ID>,segmentation-type=,segmentation-ID=\'"
                   "(--subport) option can be repeated")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            help=_("Enable trunk")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable trunk")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        trunk_id = _get_id(client, parsed_args.trunk, TRUNK)
        attrs = _get_attrs_for_trunk(self.app.client_manager, parsed_args)
        body = {TRUNK: attrs}
        try:
            client.update_trunk(trunk_id, body)
        except Exception as e:
            msg = (_("Failed to set trunk '%(t)s': %(e)s")
                   % {'t': parsed_args.trunk, 'e': e})
            raise exceptions.CommandError(msg)
        if parsed_args.set_subports:
            subport_attrs = _get_attrs_for_subports(self.app.client_manager,
                                                    parsed_args)
            try:
                client.trunk_add_subports(trunk_id, subport_attrs)
            except Exception as e:
                msg = (_("Failed to add subports to trunk '%(t)s': %(e)s")
                       % {'t': parsed_args.trunk, 'e': e})
                raise exceptions.CommandError(msg)


class ShowNetworkTrunk(command.ShowOne):
    """Show information of a given network trunk"""
    def get_parser(self, prog_name):
        parser = super(ShowNetworkTrunk, self).get_parser(prog_name)
        parser.add_argument(
            'trunk',
            metavar="<trunk>",
            help=_("Trunk to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        trunk_id = _get_id(client, parsed_args.trunk, TRUNK)
        obj = client.show_trunk(trunk_id)
        columns = _get_columns(obj[TRUNK])
        data = osc_utils.get_dict_properties(obj[TRUNK], columns,
                                             formatters=_formatters)
        return columns, data


class ListNetworkSubport(command.Lister):
    """List all subports for a given network trunk"""

    def get_parser(self, prog_name):
        parser = super(ListNetworkSubport, self).get_parser(prog_name)
        parser.add_argument(
            '--trunk',
            required=True,
            metavar="<trunk>",
            help=_("List subports belonging to this trunk (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        trunk_id = _get_id(client, parsed_args.trunk, TRUNK)
        data = client.trunk_get_subports(trunk_id)
        headers = ('Port', 'Segmentation Type', 'Segmentation ID')
        columns = ('port_id', 'segmentation_type', 'segmentation_id')
        return (headers,
                (osc_utils.get_dict_properties(
                    s, columns,
                ) for s in data[SUB_PORTS]))


class UnsetNetworkTrunk(command.Command):
    """Unset subports from a given network trunk"""

    def get_parser(self, prog_name):
        parser = super(UnsetNetworkTrunk, self).get_parser(prog_name)
        parser.add_argument(
            'trunk',
            metavar="<trunk>",
            help=_("Unset subports from this trunk (name or ID)")
        )
        parser.add_argument(
            '--subport',
            metavar="<subport>",
            required=True,
            action='append', dest='unset_subports',
            help=_("Subport to delete (name or ID of the port) "
                   "(--subport) option can be repeated")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_attrs_for_subports(self.app.client_manager, parsed_args)
        trunk_id = _get_id(client, parsed_args.trunk, TRUNK)
        client.trunk_remove_subports(trunk_id, attrs)


_formatters = {
    'admin_state_up': v2_utils.AdminStateColumn,
    'sub_ports': format_columns.ListDictColumn,
}


def _get_columns(item):
    return tuple(sorted(list(item.keys())))


def _get_attrs_for_trunk(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.description is not None:
        attrs['description'] = str(parsed_args.description)
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if 'parent_port' in parsed_args and parsed_args.parent_port is not None:
        port_id = _get_id(client_manager.neutronclient,
                          parsed_args.parent_port, 'port')
        attrs['port_id'] = port_id
    if 'add_subports' in parsed_args and parsed_args.add_subports is not None:
        attrs[SUB_PORTS] = _format_subports(client_manager,
                                            parsed_args.add_subports)

    # "trunk set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = nc_osc_utils.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    return attrs


def _format_subports(client_manager, subports):
    attrs = []
    for subport in subports:
        subport_attrs = {}
        if subport.get('port'):
            port_id = _get_id(client_manager.neutronclient,
                              subport['port'], 'port')
            subport_attrs['port_id'] = port_id
        if subport.get('segmentation-id'):
            try:
                subport_attrs['segmentation_id'] = int(
                    subport['segmentation-id'])
            except ValueError:
                msg = (_("Segmentation-id '%s' is not an integer") %
                       subport['segmentation-id'])
                raise exceptions.CommandError(msg)
        if subport.get('segmentation-type'):
            subport_attrs['segmentation_type'] = subport['segmentation-type']
        attrs.append(subport_attrs)
    return attrs


def _get_attrs_for_subports(client_manager, parsed_args):
    attrs = {}
    if 'set_subports' in parsed_args and parsed_args.set_subports is not None:
        attrs[SUB_PORTS] = _format_subports(client_manager,
                                            parsed_args.set_subports)
    if ('unset_subports' in parsed_args and
            parsed_args.unset_subports is not None):
        subports_list = []
        for subport in parsed_args.unset_subports:
            port_id = _get_id(client_manager.neutronclient,
                              subport, 'port')
            subports_list.append({'port_id': port_id})
        attrs[SUB_PORTS] = subports_list
    return attrs


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, str(id_or_name))['id']
