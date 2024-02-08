# Copyright (c) 2017 Huawei Technologies India Pvt.Limited.
# All Rights Reserved.
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

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _

LOG = logging.getLogger(__name__)

resource = 'port_pair_group'

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('port_pairs', 'Port Pair', column_util.LIST_BOTH),
    ('port_pair_group_parameters', 'Port Pair Group Parameters',
     column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('is_tap_enabled', 'Tap Enabled', column_util.LIST_BOTH)
)

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'description': 'Description',
    'port_pairs': 'Port Pair',
    'port_pair_group_parameters': 'Port Pair Group Parameters',
    'is_tap_enabled': 'Tap Enabled',
    'tenant_id': 'Project',
    'project_id': 'Project',
}


class CreateSfcPortPairGroup(command.ShowOne):
    _description = _("Create a port pair group")

    def get_parser(self, prog_name):
        parser = super(CreateSfcPortPairGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the port pair group'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the port pair group'))
        parser.add_argument(
            '--port-pair',
            metavar='<port-pair>',
            dest='port_pairs',
            default=[],
            action='append',
            help=_('Port pair (name or ID). '
                   'This option can be repeated.'))
        tap_enable = parser.add_mutually_exclusive_group()
        tap_enable.add_argument(
            '--enable-tap',
            action='store_true',
            help=_('Port pairs of this port pair group are deployed as '
                   'passive tap service function')
        )
        tap_enable.add_argument(
            '--disable-tap',
            action='store_true',
            help=_('Port pairs of this port pair group are deployed as l3 '
                   'service function (default)')
        )
        parser.add_argument(
            '--port-pair-group-parameters',
            metavar='lb-fields=<lb-fields>',
            action=parseractions.KeyValueAction,
            help=_('Dictionary of port pair group parameters. '
                   'Currently only one parameter lb-fields is supported. '
                   '<lb-fields> is a & separated list of load-balancing '
                   'fields.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        obj = client.create_sfc_port_pair_group(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteSfcPortPairGroup(command.Command):
    _description = _("Delete a given port pair group")

    def get_parser(self, prog_name):
        parser = super(DeleteSfcPortPairGroup, self).get_parser(prog_name)
        parser.add_argument(
            'port_pair_group',
            metavar='<port-pair-group>',
            nargs='+',
            help=_("Port pair group(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for ppg in parsed_args.port_pair_group:
            try:
                ppg_id = client.find_sfc_port_pair_group(
                    ppg, ignore_missing=False)['id']
                client.delete_sfc_port_pair_group(ppg_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete port pair group with name "
                            "or ID '%(ppg)s': %(e)s"), {'ppg': ppg, 'e': e})
        if result > 0:
            total = len(parsed_args.port_pair_group)
            msg = (_("%(result)s of %(total)s port pair group(s) "
                     "failed to delete.") % {'result': result,
                                             'total': total})
            raise exceptions.CommandError(msg)


class ListSfcPortPairGroup(command.Lister):
    _description = _("List port pair group")

    def get_parser(self, prog_name):
        parser = super(ListSfcPortPairGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        data = client.sfc_port_pair_groups()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers,
                (utils.get_dict_properties(
                    s, columns,
                ) for s in data))


class SetSfcPortPairGroup(command.Command):
    _description = _("Set port pair group properties")

    def get_parser(self, prog_name):
        parser = super(SetSfcPortPairGroup, self).get_parser(prog_name)
        parser.add_argument(
            'port_pair_group',
            metavar='<port-pair-group>',
            help=_("Port pair group to modify (name or ID)"))
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the port pair group'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the port pair group'))
        parser.add_argument(
            '--port-pair',
            metavar='<port-pair>',
            dest='port_pairs',
            default=[],
            action='append',
            help=_('Port pair (name or ID). '
                   'This option can be repeated.'))
        parser.add_argument(
            '--no-port-pair',
            action='store_true',
            help=_('Remove all port pair from port pair group'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        ppg_id = client.find_sfc_port_pair_group(
            parsed_args.port_pair_group)['id']
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        if parsed_args.no_port_pair:
            attrs['port_pairs'] = []
        if parsed_args.port_pairs:
            added = [client.find_sfc_port_pair(pp,
                                               ignore_missing=False)['id']
                     for pp in parsed_args.port_pairs]
            if parsed_args.no_port_pair:
                existing = []
            else:
                existing = client.find_sfc_port_pair_group(
                    parsed_args.port_pair_group,
                    ignore_missing=False)['port_pairs']
            attrs['port_pairs'] = sorted(list(set(existing) | set(added)))
        try:
            client.update_sfc_port_pair_group(ppg_id, **attrs)
        except Exception as e:
            msg = (_("Failed to update port pair group '%(ppg)s': %(e)s")
                   % {'ppg': parsed_args.port_pair_group, 'e': e})
            raise exceptions.CommandError(msg)


class ShowSfcPortPairGroup(command.ShowOne):
    _description = _("Display port pair group details")

    def get_parser(self, prog_name):
        parser = super(ShowSfcPortPairGroup, self).get_parser(prog_name)
        parser.add_argument(
            'port_pair_group',
            metavar='<port-pair-group>',
            help=_("Port pair group to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        ppg_id = client.find_sfc_port_pair_group(
            parsed_args.port_pair_group, ignore_missing=False)['id']
        obj = client.get_sfc_port_pair_group(ppg_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class UnsetSfcPortPairGroup(command.Command):
    _description = _("Unset port pairs from port pair group")

    def get_parser(self, prog_name):
        parser = super(UnsetSfcPortPairGroup, self).get_parser(prog_name)
        parser.add_argument(
            'port_pair_group',
            metavar='<port-pair-group>',
            help=_("Port pair group to unset (name or ID)"))
        port_pair_group = parser.add_mutually_exclusive_group()
        port_pair_group.add_argument(
            '--port-pair',
            action='append',
            metavar='<port-pair>',
            dest='port_pairs',
            help=_('Remove port pair(s) from the port pair group '
                   '(name or ID). This option can be repeated.'))
        port_pair_group.add_argument(
            '--all-port-pair',
            action='store_true',
            help=_('Remove all port pairs from the port pair group'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        ppg_id = client.find_sfc_port_pair_group(
            parsed_args.port_pair_group, ignore_missing=False)['id']
        attrs = {}
        if parsed_args.port_pairs:
            existing = client.find_sfc_port_pair_group(
                parsed_args.port_pair_group,
                ignore_missing=False)['port_pairs']
            removed = [client.find_sfc_port_pair(pp,
                       ignore_missing=False)['id']
                       for pp in parsed_args.port_pairs]
            attrs['port_pairs'] = list(set(existing) - set(removed))
        if parsed_args.all_port_pair:
            attrs['port_pairs'] = []
        try:
            client.update_sfc_port_pair_group(ppg_id, **attrs)
        except Exception as e:
            msg = (_("Failed to unset port pair group '%(ppg)s': %(e)s")
                   % {'ppg': parsed_args.port_pair_group, 'e': e})
            raise exceptions.CommandError(msg)


def _get_ppg_param(attrs, ppg):
    attrs['port_pair_group_parameters'] = {}
    for key, value in ppg.items():
        if key == 'lb-fields':
            attrs['port_pair_group_parameters']['lb_fields'] = ([
                field for field in value.split('&') if field])
        else:
            attrs['port_pair_group_parameters'][key] = value
    return attrs['port_pair_group_parameters']


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    client = client_manager.network
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.port_pairs:
        attrs['port_pairs'] = [client.find_sfc_port_pair(
            pp, ignore_missing=False)['id']
                               for pp in parsed_args.port_pairs]

    if is_create:
        _get_attrs(attrs, parsed_args)
    return attrs


def _get_attrs(attrs, parsed_args):
    if parsed_args.port_pair_group_parameters is not None:
        attrs['port_pair_group_parameters'] = (
            _get_ppg_param(attrs, parsed_args.port_pair_group_parameters))
    if parsed_args.enable_tap:
        attrs['tap_enabled'] = True
    if parsed_args.disable_tap:
        attrs['tap_enabled'] = False
