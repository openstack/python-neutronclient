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

resource = 'port_chain'

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('port_pair_groups', 'Port Pair Groups', column_util.LIST_BOTH),
    ('flow_classifiers', 'Flow Classifiers',
     column_util.LIST_BOTH),
    ('chain_parameters', 'Chain Parameters',
     column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
)

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'port_pair_groups': 'Port Pair Groups',
    'flow_classifiers': 'Flow Classifiers',
    'chain_parameters': 'Chain Parameters',
    'description': 'Description',
    'tenant_id': 'Project',
    'project_id': 'Project',
}


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
                   'correlation=(mpls|nsh) (default is mpls) '
                   'and symmetric=(true|false).'))
        parser.add_argument(
            '--port-pair-group',
            metavar='<port-pair-group>',
            dest='port_pair_groups',
            required=True,
            action='append',
            help=_('Add port pair group (name or ID). '
                   'This option can be repeated.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        obj = client.create_sfc_port_chain(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteSfcPortChain(command.Command):
    _description = _("Delete a given port chain")

    def get_parser(self, prog_name):
        parser = super(DeleteSfcPortChain, self).get_parser(prog_name)
        parser.add_argument(
            'port_chain',
            metavar="<port-chain>",
            nargs='+',
            help=_("Port chain(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for pc in parsed_args.port_chain:
            try:
                pc_id = client.find_sfc_port_chain(
                    pc, ignore_missing=False)['id']
                client.delete_sfc_port_chain(pc_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete port chain with name "
                            "or ID '%(pc)s': %(e)s"), {'pc': pc, 'e': e})
        if result > 0:
            total = len(parsed_args.port_chain)
            msg = (_("%(result)s of %(total)s port chain(s) "
                     "failed to delete.") % {'result': result,
                                             'total': total})
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
        client = self.app.client_manager.network
        data = client.sfc_port_chains()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers,
                (utils.get_dict_properties(s, columns)
                 for s in data))


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
            help=_('Remove associated flow classifiers from the port chain'))
        parser.add_argument(
            '--port-pair-group',
            metavar='<port-pair-group>',
            dest='port_pair_groups',
            action='append',
            help=_('Add port pair group (name or ID). '
                   'Current port pair groups order is kept, the added port '
                   'pair group will be placed at the end of the port chain. '
                   'This option can be repeated.'))
        parser.add_argument(
            '--no-port-pair-group',
            action='store_true',
            help=_('Remove associated port pair groups from the port chain. '
                   'At least one --port-pair-group must be specified '
                   'together.'))
        parser.add_argument(
            'port_chain',
            metavar='<port-chain>',
            help=_("Port chain to modify (name or ID)"))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        pc_id = client.find_sfc_port_chain(parsed_args.port_chain,
                                           ignore_missing=False)['id']
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        if parsed_args.no_flow_classifier:
            attrs['flow_classifiers'] = []
        if parsed_args.flow_classifiers:
            if parsed_args.no_flow_classifier:
                fc_list = []
            else:
                fc_list = client.find_sfc_port_chain(
                    parsed_args.port_chain,
                    ignore_missing=False
                )['flow_classifiers']
            for fc in parsed_args.flow_classifiers:
                fc_id = client.find_sfc_flow_classifier(
                    fc,
                    ignore_missing=False)['id']
                if fc_id not in fc_list:
                    fc_list.append(fc_id)
            attrs['flow_classifiers'] = fc_list
        if (parsed_args.no_port_pair_group and not
                parsed_args.port_pair_groups):
            message = _('At least one --port-pair-group must be specified.')
            raise exceptions.CommandError(message)
        if parsed_args.no_port_pair_group and parsed_args.port_pair_groups:
            ppg_list = []
            for ppg in parsed_args.port_pair_groups:
                ppg_id = client.find_sfc_port_pair_group(
                    ppg, ignore_missing=False)['id']
                if ppg_id not in ppg_list:
                    ppg_list.append(ppg_id)
            attrs['port_pair_groups'] = ppg_list
        if (parsed_args.port_pair_groups and
                not parsed_args.no_port_pair_group):
            ppg_list = client.find_sfc_port_chain(
                parsed_args.port_chain,
                ignore_missing=False
            )['port_pair_groups']
            for ppg in parsed_args.port_pair_groups:
                ppg_id = client.find_sfc_port_pair_group(
                    ppg, ignore_missing=False)['id']
                if ppg_id not in ppg_list:
                    ppg_list.append(ppg_id)
            attrs['port_pair_groups'] = ppg_list
        try:
            client.update_sfc_port_chain(pc_id, **attrs)
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
        client = self.app.client_manager.network
        pc_id = client.find_sfc_port_chain(parsed_args.port_chain,
                                           ignore_missing=False)['id']
        obj = client.get_sfc_port_chain(pc_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
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
        client = self.app.client_manager.network
        pc_id = client.find_sfc_port_chain(parsed_args.port_chain,
                                           ignore_missing=False)['id']
        attrs = {}
        if parsed_args.flow_classifiers:
            fc_list = client.find_sfc_port_chain(
                parsed_args.port_chain, ignore_missing=False
            )['flow_classifiers']
            for fc in parsed_args.flow_classifiers:
                fc_id = client.find_sfc_flow_classifier(
                    fc,
                    ignore_missing=False)['id']
                if fc_id in fc_list:
                    fc_list.remove(fc_id)
            attrs['flow_classifiers'] = fc_list
        if parsed_args.all_flow_classifier:
            attrs['flow_classifiers'] = []
        if parsed_args.port_pair_groups:
            ppg_list = client.find_sfc_port_chain(
                parsed_args.port_chain,
                ignore_missing=False)['port_pair_groups']
            for ppg in parsed_args.port_pair_groups:
                ppg_id = client.find_sfc_port_pair_group(
                    ppg,
                    ignore_missing=False)['id']
                if ppg_id in ppg_list:
                    ppg_list.remove(ppg_id)
            if ppg_list == []:
                message = _('At least one port pair group must be'
                            ' specified.')
                raise exceptions.CommandError(message)
            attrs['port_pair_groups'] = ppg_list
        try:
            client.update_sfc_port_chain(pc_id, **attrs)
        except Exception as e:
            msg = (_("Failed to unset port chain '%(pc)s': %(e)s")
                   % {'pc': parsed_args.port_chain, 'e': e})
            raise exceptions.CommandError(msg)


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    client = client_manager.network
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.port_pair_groups:
        attrs['port_pair_groups'] = [client.find_sfc_port_pair_group(
            ppg, ignore_missing=False)['id']
                                     for ppg in parsed_args.port_pair_groups]
    if parsed_args.flow_classifiers:
        attrs['flow_classifiers'] = [client.find_sfc_flow_classifier(
            fc, ignore_missing=False)['id']
                                     for fc in parsed_args.flow_classifiers]
    if is_create is True:
        _get_attrs(attrs, parsed_args)
    return attrs


def _get_attrs(attrs, parsed_args):
    if parsed_args.chain_parameters is not None:
        chain_params = {}
        for chain_param in parsed_args.chain_parameters:
            if 'correlation' in chain_param:
                chain_params['correlation'] = chain_param['correlation']
            if 'symmetric' in chain_param:
                chain_params['symmetric'] = chain_param['symmetric']
        attrs['chain_parameters'] = chain_params
