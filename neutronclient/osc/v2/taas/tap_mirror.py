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

from osc_lib.cli import identity as identity_utils
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient.network.v2 import port as osc_port

from neutronclient._i18n import _
from neutronclient.osc.v2.taas import tap_service


LOG = logging.getLogger(__name__)

TAP_MIRROR = 'tap_mirror'
TAP_MIRRORS = '%ss' % TAP_MIRROR

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('tenant_id', 'Tenant', column_util.LIST_LONG_ONLY),
    ('name', 'Name', column_util.LIST_BOTH),
    ('port_id', 'Port', column_util.LIST_BOTH),
    ('directions', 'Directions', column_util.LIST_LONG_ONLY),
    ('remote_ip', 'Remote IP', column_util.LIST_BOTH),
    ('mirror_type', 'Mirror Type', column_util.LIST_LONG_ONLY),
)


def _get_columns(item):
    column_map = {}
    hidden_columns = ['location', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item,
        column_map,
        hidden_columns
    )


class CreateTapMirror(command.ShowOne):
    _description = _("Create a Tap Mirror")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        identity_utils.add_project_owner_option_to_parser(parser)
        tap_service._add_updatable_args(parser)
        parser.add_argument(
            '--port',
            dest='port_id',
            required=True,
            metavar="PORT",
            help=_('Port to which the Tap Mirror is connected.'))
        parser.add_argument(
            '--directions',
            dest='directions',
            action=osc_port.JSONKeyValueAction,
            required=True,
            help=_('A dictionary of direction and tunnel_id. Direction can '
                   'be IN and OUT.'))
        parser.add_argument(
            '--remote-ip',
            dest='remote_ip',
            required=True,
            help=_('The remote IP of the Tap Mirror, this will be the '
                   'remote end of the GRE or ERSPAN v1 tunnel'))
        parser.add_argument(
            '--mirror-type',
            dest='mirror_type',
            required=True,
            help=_('The type of the mirroring, it can be gre or erspanv1'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            attrs['description'] = str(parsed_args.description)
        if parsed_args.port_id is not None:
            port_id = client.find_port(parsed_args.port_id)['id']
            attrs['port_id'] = port_id
        if parsed_args.directions is not None:
            attrs['directions'] = parsed_args.directions
        if parsed_args.remote_ip is not None:
            attrs['remote_ip'] = parsed_args.remote_ip
        if parsed_args.mirror_type is not None:
            attrs['mirror_type'] = parsed_args.mirror_type
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = identity_utils.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id
        obj = client.create_tap_mirror(**attrs)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class ListTapMirror(command.Lister):
    _description = _("List Tap Mirrors that belong to a given tenant")

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
        objs = client.tap_mirrors(retrieve_all=True, params=params)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=True)
        return (headers, (osc_utils.get_dict_properties(
            s, columns) for s in objs))


class ShowTapMirror(command.ShowOne):
    _description = _("Show information of a given Tap Mirror")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_MIRROR,
            metavar="<%s>" % TAP_MIRROR,
            help=_("ID or name of Tap Mirror to look up."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_tap_mirror(parsed_args.tap_mirror,
                                    ignore_missing=False).id
        obj = client.get_tap_mirror(id)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteTapMirror(command.Command):
    _description = _("Delete a Tap Mirror")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_MIRROR,
            metavar="<%s>" % TAP_MIRROR,
            nargs="+",
            help=_("ID(s) or name(s) of the Tap Mirror to delete."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fails = 0
        for id_or_name in parsed_args.tap_mirror:
            try:
                id = client.find_tap_mirror(id_or_name,
                                            ignore_missing=False).id

                client.delete_tap_mirror(id)
                LOG.warning("Tap Mirror %(id)s deleted", {'id': id})
            except Exception as e:
                fails += 1
                LOG.error("Failed to delete Tap Mirror with name or ID "
                          "'%(id_or_name)s': %(e)s",
                          {'id_or_name': id_or_name, 'e': e})
        if fails > 0:
            msg = (_("Failed to delete %(fails)s of %(total)s Tap Mirror.") %
                   {'fails': fails, 'total': len(parsed_args.tap_mirror)})
            raise exceptions.CommandError(msg)


class UpdateTapMirror(command.ShowOne):
    _description = _("Update a Tap Mirror.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_MIRROR,
            metavar="<%s>" % TAP_MIRROR,
            help=_("ID or name of the Tap Mirror to update."),
        )
        tap_service._add_updatable_args(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        original_t_s = client.find_tap_mirror(parsed_args.tap_mirror,
                                              ignore_missing=False).id
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            attrs['description'] = str(parsed_args.description)
        obj = client.update_tap_mirror(original_t_s, **attrs)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data
