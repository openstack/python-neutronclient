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

from osc_lib.cli import identity as identity_utils
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _


LOG = logging.getLogger(__name__)

TAP_SERVICE = 'tap_service'
TAP_SERVICES = '%ss' % TAP_SERVICE

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('tenant_id', 'Tenant', column_util.LIST_LONG_ONLY),
    ('name', 'Name', column_util.LIST_BOTH),
    ('port_id', 'Port', column_util.LIST_BOTH),
    ('status', 'Status', column_util.LIST_BOTH),
)


def _add_updatable_args(parser):
    parser.add_argument(
        '--name',
        help=_('Name of this Tap service.'))
    parser.add_argument(
        '--description',
        help=_('Description for this Tap service.'))


def _updatable_args2body(parsed_args, body):
    for attribute in ['name', 'description']:
        if (hasattr(parsed_args, attribute) and
                getattr(parsed_args, attribute) is not None):
            body[attribute] = getattr(parsed_args, attribute)


def _get_columns(item):
    column_map = {}
    hidden_columns = ['location', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item,
        column_map,
        hidden_columns
    )


class CreateTapService(command.ShowOne):
    _description = _("Create a tap service")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        identity_utils.add_project_owner_option_to_parser(parser)
        _add_updatable_args(parser)
        parser.add_argument(
            '--port',
            dest='port_id',
            required=True,
            metavar="PORT",
            help=_('Port to which the Tap service is connected.'))
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
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = identity_utils.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id
        obj = client.create_tap_service(**attrs)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class ListTapService(command.Lister):
    _description = _("List tap services that belong to a given tenant")

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
        objs = client.tap_services(retrieve_all=True, params=params)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=True)
        return (headers, (osc_utils.get_dict_properties(
            s, columns) for s in objs))


class ShowTapService(command.ShowOne):
    _description = _("Show information of a given tap service")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_SERVICE,
            metavar="<%s>" % TAP_SERVICE,
            help=_("ID or name of tap service to look up."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_tap_service(parsed_args.tap_service,
                                     ignore_missing=False).id
        obj = client.get_tap_service(id)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteTapService(command.Command):
    _description = _("Delete a tap service")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_SERVICE,
            metavar="<%s>" % TAP_SERVICE,
            nargs="+",
            help=_("ID(s) or name(s) of tap service to delete."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fails = 0
        for id_or_name in parsed_args.tap_service:
            try:
                id = client.find_tap_service(id_or_name,
                                             ignore_missing=False).id

                client.delete_tap_service(id)
                LOG.warning("Tap service %(id)s deleted", {'id': id})
            except Exception as e:
                fails += 1
                LOG.error("Failed to delete tap service with name or ID "
                          "'%(id_or_name)s': %(e)s",
                          {'id_or_name': id_or_name, 'e': e})
        if fails > 0:
            msg = (_("Failed to delete %(fails)s of %(total)s tap service.") %
                   {'fails': fails, 'total': len(parsed_args.tap_service)})
            raise exceptions.CommandError(msg)


class UpdateTapService(command.ShowOne):
    _description = _("Update a tap service.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_SERVICE,
            metavar="<%s>" % TAP_SERVICE,
            help=_("ID or name of tap service to update."),
        )
        _add_updatable_args(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        original_t_s = client.find_tap_service(parsed_args.tap_service,
                                               ignore_missing=False).id
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.description is not None:
            attrs['description'] = str(parsed_args.description)
        obj = client.update_tap_service(original_t_s, **attrs)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data
