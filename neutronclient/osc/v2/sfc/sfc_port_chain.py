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

from neutronclient._i18n import _
from neutronclient.osc import utils as nc_osc_utils

LOG = logging.getLogger(__name__)

resource = 'port_chain'

_attr_map = (
    ('id', 'ID', nc_osc_utils.LIST_BOTH),
    ('name', 'Name', nc_osc_utils.LIST_BOTH),
    ('port_pair_groups', 'Port Pair Groups', nc_osc_utils.LIST_BOTH),
    ('flow_classifiers', 'Flow Classifiers',
     nc_osc_utils.LIST_BOTH),
    ('chain_parameters', 'Chain Parameters',
     nc_osc_utils.LIST_BOTH),
    ('description', 'Description', nc_osc_utils.LIST_LONG_ONLY),
    ('chain_id', 'Chain ID',  nc_osc_utils.LIST_BOTH),
    ('project_id', 'Project', nc_osc_utils.LIST_LONG_ONLY),
)


class CreateSfcPortChain(command.ShowOne):
    _description = _("Create a port chain")

    def get_parser(self, prog_name):
        parser = super(CreateSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the port chain'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the port chain'))
        parser.add_argument(
            '--flow-classifier',
            default=[],
            metavar='<flow-classifier>',
            dest='flow_classifiers',
            action='append',
            help=_('Add flow classifier (name or ID). '
                   'This option can be repeated.'))
        parser.add_argument(
            '--chain-parameters',
            metavar='correlation=<correlation-type>,symmetric=<boolean>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['correlation', 'symmetric'],
            help=_('Dictionary of chain parameters. Supports '
                   'correlation=mpls and symmetric=true|false.'))
        parser.add_argument(
            '--port-pair-group',
            metavar='<port-pair-group>',
            dest='port_pair_groups',
            required=True,
            action='append',
            help=_('Port pair group (name or ID). '
                   'This option can be repeated.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        body = {resource: attrs}
        obj = client.create_port_chain(body)[resource]
        columns, display_columns = nc_osc_utils.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteSfcPortChain(command.Command):
    _description = _("Delete a given port chain")

    def get_parser(self, prog_name):
        parser = super(DeleteSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            'port_chain',
            metavar="<port-chain>",
            help=_("Port chain to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        # TODO(mohan): Add support for deleting multiple resources.
        client = self.app.client_manager.neutronclient
        pc_id = _get_id(client, parsed_args.port_chain, resource)
        try:
            client.delete_port_chain(pc_id)
        except Exception as e:
            msg = (_("Failed to delete port chain with name "
                     "or ID '%(pc)s': %(e)s")
                   % {'pc': parsed_args.port_chain, 'e': e})
            raise exceptions.CommandError(msg)


class ListSfcPortChain(command.Lister):
    _description = _("List port chains")

    def get_parser(self, prog_name):
        parser = super(ListSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        data = client.list_port_chain()
        headers, columns = nc_osc_utils.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers,
                (utils.get_dict_properties(s, columns)
                 for s in data['port_chains']))


class SetSfcPortChain(command.Command):
    _description = _("Set port chain properties")

    def get_parser(self, prog_name):
        parser = super(SetSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the port chain'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the port chain'))
        parser.add_argument(
            '--flow-classifier',
            metavar='<flow-classifier>',
            dest='flow_classifiers',
            action='append',
            help=_('Add flow classifier (name or ID). '
                   'This option can be repeated.'))
        parser.add_argument(
            '--no-flow-classifier',
            action='store_true',
            help=_('Associate no flow classifier with the port chain'))
        parser.add_argument(
            '--port-pair-group',
            metavar='<port-pair-group>',
            dest='port_pair_groups',
            action='append',
            help=_('Add port pair group (name or ID). '
                   'This option can be repeated.'))
        parser.add_argument(
            '--no-port-pair-group',
            action='store_true',
            help=_('Remove associated port pair group from the port chain.'
                   'At least one --port-pair-group must be specified '
                   'together.'))
        parser.add_argument(
            'port_chain',
            metavar='<port-chain>',
            help=_("Port chain to modify (name or ID)"))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        pc_id = _get_id(client, parsed_args.port_chain, resource)
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        if parsed_args.no_flow_classifier:
            attrs['flow_classifiers'] = []
        if parsed_args.flow_classifiers:
            for fc in parsed_args.flow_classifiers:
                added = [client.find_resource(
                    'flow_classifier', fc,
                    cmd_resource='sfc_flow_classifier')['id']]
            if parsed_args.no_flow_classifier:
                existing = []
            else:
                existing = [client.find_resource(
                    resource, parsed_args.port_chain,
                    cmd_resource='sfc_port_chain')['flow_classifiers']]
            attrs['flow_classifiers'] = sorted(list(
                set(existing) | set(added)))
        if (parsed_args.no_port_pair_group and not
                parsed_args.port_pair_groups):
            message = _('At least one --port-pair-group must be specified.')
            raise exceptions.CommandError(message)
        if parsed_args.no_port_pair_group and parsed_args.port_pair_groups:
            for ppg in parsed_args.port_pair_groups:
                attrs['port_pair_groups'] = [client.find_resource(
                    'port_pair_group', ppg,
                    cmd_resource='sfc_port_pair_group')['id']]
        if (parsed_args.port_pair_groups and
                not parsed_args.no_port_pair_group):
            existing_ppg = [client.find_resource(
                resource, parsed_args.port_chain,
                cmd_resource='sfc_port_chain')['port_pair_groups']]
            for ppg in parsed_args.port_pair_groups:
                existing_ppg.append(client.find_resource(
                    'port_pair_group', ppg,
                    cmd_resource='sfc_port_pair_group')['id'])
                attrs['port_pair_groups'] = sorted(list(set(existing_ppg)))
        body = {resource: attrs}
        try:
            client.update_port_chain(pc_id, body)
        except Exception as e:
            msg = (_("Failed to update port chain '%(pc)s': %(e)s")
                   % {'pc': parsed_args.port_chain, 'e': e})
            raise exceptions.CommandError(msg)


class ShowSfcPortChain(command.ShowOne):
    _description = _("Display port chain details")

    def get_parser(self, prog_name):
        parser = super(ShowSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            'port_chain',
            metavar="<port-chain>",
            help=_("Port chain to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        pc_id = _get_id(client, parsed_args.port_chain, resource)
        obj = client.show_port_chain(pc_id)[resource]
        columns, display_columns = nc_osc_utils.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class UnsetSfcPortChain(command.Command):
    _description = _("Unset port chain properties")

    def get_parser(self, prog_name):
        parser = super(UnsetSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            'port_chain',
            metavar='<port-chain>',
            help=_("Port chain to unset (name or ID)"))
        port_chain = parser.add_mutually_exclusive_group()
        port_chain.add_argument(
            '--flow-classifier',
            action='append',
            metavar='<flow-classifier>',
            dest='flow_classifiers',
            help=_('Remove flow classifier(s) from the port chain '
                   '(name or ID). This option can be repeated.'))
        port_chain.add_argument(
            '--all-flow-classifier',
            action='store_true',
            help=_('Remove all flow classifiers from the port chain'))
        parser.add_argument(
            '--port-pair-group',
            metavar='<port-pair-group>',
            dest='port_pair_groups',
            action='append',
            help=_('Remove port pair group(s) from the port chain '
                   '(name or ID). This option can be repeated.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        pc_id = _get_id(client, parsed_args.port_chain, resource)
        attrs = {}
        if parsed_args.flow_classifiers:
            existing = [client.find_resource(
                resource, parsed_args.port_chain,
                cmd_resource='sfc_port_chain')['flow_classifiers']]
            for fc in parsed_args.flow_classifiers:
                removed = [client.find_resource(
                    'flow_classifier', fc,
                    cmd_resource='sfc_flow_classifier')['id']]
                attrs['flow_classifiers'] = list(set(existing) - set(removed))
        if parsed_args.all_flow_classifier:
            attrs['flow_classifiers'] = []
        if parsed_args.port_pair_groups:
            existing_ppg = [client.find_resource(
                resource, parsed_args.port_chain,
                cmd_resource='sfc_port_chain')['port_pair_groups']]
            for ppg in parsed_args.port_pair_groups:
                removed_ppg = [client.find_resource(
                    'port_pair_group', ppg,
                    cmd_resource='sfc_port_pair_group')['id']]
            attrs['port_pair_groups'] = list(set(existing_ppg) -
                                             set(removed_ppg))
            if attrs['port_pair_groups'] == []:
                message = _('At least one --port-pair-group must be'
                            ' specified.')
                raise exceptions.CommandError(message)
        body = {resource: attrs}
        try:
            client.update_port_chain(pc_id, body)
        except Exception as e:
            msg = (_("Failed to unset port chain '%(pc)s': %(e)s")
                   % {'pc': parsed_args.port_chain, 'e': e})
            raise exceptions.CommandError(msg)


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if ('port_pair_groups' in parsed_args and
            parsed_args.port_pair_groups is not None):
        attrs['port_pair_groups'] = [(_get_id(client_manager.neutronclient,
                                              ppg, 'port_pair_group'))
                                     for ppg in parsed_args.port_pair_groups]
    if ('flow_classifiers' in parsed_args and
            parsed_args.flow_classifiers is not None):
        attrs['flow_classifiers'] = [(_get_id(client_manager.neutronclient, fc,
                                      'flow_classifier'))
                                     for fc in parsed_args.flow_classifiers]
    if is_create is True:
        _get_attrs(attrs, parsed_args)
    return attrs


def _get_attrs(attrs, parsed_args):
    if 'chain_parameters' in parsed_args:
        attrs['chain_parameters'] = parsed_args.chain_parameters


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, id_or_name)['id']
