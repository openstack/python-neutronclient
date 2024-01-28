# Copyright 2017 Intel Corporation.
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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _

LOG = logging.getLogger(__name__)

resource = 'service_graph'

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('port_chains', 'Branching Points', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
)

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'description': 'Description',
    'port_chains': 'Branching Points',
    'tenant_id': 'Project',
    'project_id': 'Project',
}


class CreateSfcServiceGraph(command.ShowOne):
    """Create a service graph."""
    def get_parser(self, prog_name):
        parser = super(CreateSfcServiceGraph, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the service graph.'))
        parser.add_argument(
            '--description',
            help=_('Description for the service graph.'))
        parser.add_argument(
            '--branching-point',
            metavar='SRC_CHAIN:DST_CHAIN_1,DST_CHAIN_2,DST_CHAIN_N',
            dest='branching_points',
            action='append',
            default=[], required=True,
            help=_('Service graph branching point: the key is the source '
                   'Port Chain while the value is a list of destination '
                   'Port Chains. This option can be repeated.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        try:
            obj = client.create_sfc_service_graph(**attrs)
            display_columns, columns = \
                utils.get_osc_show_columns_for_sdk_resource(
                    obj, _attr_map_dict, ['location', 'tenant_id'])
            data = utils.get_dict_properties(obj, columns)
            return display_columns, data
        except Exception as e:
            msg = (_("Failed to create service graph using '%(pcs)s': %(e)s")
                   % {'pcs': parsed_args.branching_points, 'e': e})
            raise exceptions.CommandError(msg)


class SetSfcServiceGraph(command.Command):
    _description = _("Set service graph properties")

    def get_parser(self, prog_name):
        parser = super(SetSfcServiceGraph, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the service graph'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the service graph'))
        parser.add_argument(
            'service_graph',
            metavar='<service-graph>',
            help=_("Service graph to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        service_graph_id = client.find_sfc_service_graph(
            parsed_args.service_graph, ignore_missing=False)['id']
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        try:
            client.update_sfc_service_graph(service_graph_id, **attrs)
        except Exception as e:
            msg = (_("Failed to update service graph "
                     "'%(service_graph)s': %(e)s")
                   % {'service_graph': parsed_args.service_graph, 'e': e})
            raise exceptions.CommandError(msg)


class DeleteSfcServiceGraph(command.Command):
    """Delete a given service graph."""

    def get_parser(self, prog_name):
        parser = super(DeleteSfcServiceGraph, self).get_parser(prog_name)
        parser.add_argument(
            'service_graph',
            metavar="<service-graph>",
            nargs='+',
            help=_("ID or name of the service graph(s) to delete.")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for sg in parsed_args.service_graph:
            try:
                sg_id = client.find_sfc_service_graph(
                    sg, ignore_missing=False)['id']
                client.delete_sfc_service_graph(sg_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete service graph with name "
                            "or ID '%(sg)s': %(e)s"),
                          {'sg': sg, 'e': e})
        if result > 0:
            total = len(parsed_args.service_graph)
            msg = (_("%(result)s of %(total)s service graph(s) "
                     "failed to delete.") % {'result': result,
                                             'total': total})
            raise exceptions.CommandError(msg)


class ListSfcServiceGraph(command.Lister):
    _description = _("List service graphs")

    def get_parser(self, prog_name):
        parser = super(ListSfcServiceGraph, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        data = client.sfc_service_graphs()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers,
                (utils.get_dict_properties(s, columns)
                 for s in data))


class ShowSfcServiceGraph(command.ShowOne):
    """Show information of a given service graph."""

    def get_parser(self, prog_name):
        parser = super(ShowSfcServiceGraph, self).get_parser(prog_name)
        parser.add_argument(
            'service_graph',
            metavar="<service-graph>",
            help=_("ID or name of the service graph to display.")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        sg_id = client.find_sfc_service_graph(parsed_args.service_graph,
                                              ignore_missing=False)['id']
        obj = client.get_sfc_service_graph(sg_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.description is not None:
        attrs['description'] = str(parsed_args.description)
    if is_create:
        _get_attrs_for_create(client_manager, attrs, parsed_args)
    return attrs


def _validate_destination_chains(comma_split, attrs, client, sc_):
    for e in comma_split:
        if e != "":
            dc_ = client.find_sfc_port_chain(e, ignore_missing=False)['id']
            attrs['port_chains'][sc_].append(dc_)
            if _check_cycle(attrs['port_chains'], sc_, dc_):
                raise exceptions.CommandError(
                    "Error: Service graph contains a cycle")
        else:
            raise exceptions.CommandError(
                "Error: you must specify at least one "
                "destination chain for each source chain")
    return attrs


def _check_cycle(graph, new_src, new_dest):
    for src in graph:
        if src == new_dest:
            if _visit(graph, src, new_dest, new_src):
                return True
    return False


def _visit(graph, src, new_dest, new_src):
    if src in graph:
        found_cycle = False
        for dest in graph[src]:
            if new_src == dest or found_cycle:
                return True
            else:
                found_cycle = _visit(graph, dest, new_dest, new_src)
    return False


def _get_attrs_for_create(client_manager, attrs, parsed_args):
    client = client_manager.network
    if parsed_args.branching_points:
        attrs['port_chains'] = {}
        src_chain = None
        for c in parsed_args.branching_points:
            if ':' not in c:
                raise exceptions.CommandError(
                    "Error: You must specify at least one "
                    "destination chain for each source chain.")
            colon_split = c.split(':')
            src_chain = colon_split.pop(0)
            sc_ = client.find_sfc_port_chain(src_chain,
                                             ignore_missing=False)['id']
            for i in colon_split:
                comma_split = i.split(',')
                unique = set(comma_split)
                if len(unique) != len(comma_split):
                    raise exceptions.CommandError(
                        "Error: Duplicate "
                        "destination chains from "
                        "source chain {}".format(src_chain))
                if sc_ in attrs['port_chains']:
                    raise exceptions.CommandError(
                        "Error: Source chain {} is in "
                        "use already ".format(src_chain))
                attrs['port_chains'][sc_] = []
                _validate_destination_chains(
                    comma_split, attrs, client, sc_)
