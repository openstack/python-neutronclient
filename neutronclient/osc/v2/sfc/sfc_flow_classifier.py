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

import argparse
import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.common import exceptions as nc_exc

LOG = logging.getLogger(__name__)

resource = 'flow_classifier'

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('summary', 'Summary', column_util.LIST_SHORT_ONLY),
    ('protocol', 'Protocol', column_util.LIST_LONG_ONLY),
    ('ethertype', 'Ethertype', column_util.LIST_LONG_ONLY),
    ('source_ip_prefix', 'Source IP',
     column_util.LIST_LONG_ONLY),
    ('destination_ip_prefix', 'Destination IP',
     column_util.LIST_LONG_ONLY),
    ('logical_source_port', 'Logical Source Port',
     column_util.LIST_LONG_ONLY),
    ('logical_destination_port', 'Logical Destination Port',
     column_util.LIST_LONG_ONLY),
    ('source_port_range_min', 'Source Port Range Min',
     column_util.LIST_LONG_ONLY),
    ('source_port_range_max', 'Source Port Range Max',
     column_util.LIST_LONG_ONLY),
    ('destination_port_range_min', 'Destination Port Range Min',
     column_util.LIST_LONG_ONLY),
    ('destination_port_range_max', 'Destination Port Range Max',
     column_util.LIST_LONG_ONLY),
    ('l7_parameters', 'L7 Parameters', column_util.LIST_LONG_ONLY),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
)


class CreateSfcFlowClassifier(command.ShowOne):
    _description = _("Create a flow classifier")

    def get_parser(self, prog_name):
        parser = super(CreateSfcFlowClassifier, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the flow classifier'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the flow classifier'))
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            help=_('IP protocol name. Protocol name should be as per '
                   'IANA standard.'))
        parser.add_argument(
            '--ethertype',
            metavar='{IPv4,IPv6}',
            default='IPv4', choices=['IPv4', 'IPv6'],
            help=_('L2 ethertype, default is IPv4'))
        parser.add_argument(
            '--source-port',
            metavar='<min-port>:<max-port>',
            help=_('Source protocol port (allowed range [1,65535]. Must be '
                   'specified as a:b, where a=min-port and b=max-port) '
                   'in the allowed range.'))
        parser.add_argument(
            '--destination-port',
            metavar='<min-port>:<max-port>',
            help=_('Destination protocol port (allowed range [1,65535]. Must '
                   'be specified as a:b, where a=min-port and b=max-port) '
                   'in the allowed range.'))
        parser.add_argument(
            '--source-ip-prefix',
            metavar='<source-ip-prefix>',
            help=_('Source IP address in CIDR notation'))
        parser.add_argument(
            '--destination-ip-prefix',
            metavar='<destination-ip-prefix>',
            help=_('Destination IP address in CIDR notation'))
        parser.add_argument(
            '--logical-source-port',
            metavar='<logical-source-port>',
            help=_('Neutron source port (name or ID)'))
        parser.add_argument(
            '--logical-destination-port',
            metavar='<logical-destination-port>',
            help=_('Neutron destination port (name or ID)'))
        parser.add_argument(
            '--l7-parameters',
            help=_('Dictionary of L7 parameters. Currently, no value is '
                   'supported for this option.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        body = {resource: attrs}
        obj = client.create_sfc_flow_classifier(body)[resource]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteSfcFlowClassifier(command.Command):
    _description = _("Delete a given flow classifier")

    def get_parser(self, prog_name):
        parser = super(DeleteSfcFlowClassifier, self).get_parser(prog_name)
        parser.add_argument(
            'flow_classifier',
            metavar='<flow-classifier>',
            help=_("Flow classifier to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        # TODO(mohan): Add support for deleting multiple resources.
        client = self.app.client_manager.neutronclient
        fc_id = _get_id(client, parsed_args.flow_classifier, resource)
        try:
            client.delete_sfc_flow_classifier(fc_id)
        except Exception as e:
            msg = (_("Failed to delete flow classifier with name "
                     "or ID '%(fc)s': %(e)s")
                   % {'fc': parsed_args.flow_classifier, 'e': e})
            raise exceptions.CommandError(msg)


class ListSfcFlowClassifier(command.Lister):
    _description = _("List flow classifiers")

    def get_parser(self, prog_name):
        parser = super(ListSfcFlowClassifier, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        return parser

    def extend_list(self, data, parsed_args):
        ext_data = data['flow_classifiers']
        for d in ext_data:
            val = []
            protocol = d['protocol'].upper() if d['protocol'] else 'any'
            val.append('protocol: ' + protocol)
            val.append(self._get_protocol_port_details(d, 'source'))
            val.append(self._get_protocol_port_details(d, 'destination'))
            if 'logical_source_port' in d:
                val.append('neutron_source_port: ' +
                           str(d['logical_source_port']))

            if 'logical_destination_port' in d:
                val.append('neutron_destination_port: ' +
                           str(d['logical_destination_port']))

            if 'l7_parameters' in d:
                l7_param = 'l7_parameters: {%s}' % ','.join(d['l7_parameters'])
                val.append(l7_param)
            d['summary'] = ',\n'.join(val)
        return ext_data

    def _get_protocol_port_details(self, data, val):
        type_ip_prefix = val + '_ip_prefix'
        ip_prefix = data.get(type_ip_prefix)
        if not ip_prefix:
            ip_prefix = 'any'
        min_port = data.get(val + '_port_range_min')
        if min_port is None:
            min_port = 'any'
        max_port = data.get(val + '_port_range_max')
        if max_port is None:
            max_port = 'any'
        return '%s[port]: %s[%s:%s]' % (
            val, ip_prefix, min_port, max_port)

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        obj = client.list_sfc_flow_classifiers()
        obj_extend = self.extend_list(obj, parsed_args)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(
            s, columns) for s in obj_extend))


class SetSfcFlowClassifier(command.Command):
    _description = _("Set flow classifier properties")

    def get_parser(self, prog_name):
        parser = super(SetSfcFlowClassifier, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the flow classifier'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description for the flow classifier'))
        parser.add_argument(
            'flow_classifier',
            metavar='<flow-classifier>',
            help=_("Flow classifier to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        fc_id = _get_id(client, parsed_args.flow_classifier, resource)
        attrs = _get_common_attrs(self.app.client_manager, parsed_args,
                                  is_create=False)
        body = {resource: attrs}
        try:
            client.update_sfc_flow_classifier(fc_id, body)
        except Exception as e:
            msg = (_("Failed to update flow classifier '%(fc)s': %(e)s")
                   % {'fc': parsed_args.flow_classifier, 'e': e})
            raise exceptions.CommandError(msg)


class ShowSfcFlowClassifier(command.ShowOne):
    _description = _("Display flow classifier details")

    def get_parser(self, prog_name):
        parser = super(ShowSfcFlowClassifier, self).get_parser(prog_name)
        parser.add_argument(
            'flow_classifier',
            metavar='<flow-classifier>',
            help=_("Flow classifier to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        fc_id = _get_id(client, parsed_args.flow_classifier, resource)
        obj = client.show_sfc_flow_classifier(fc_id)[resource]
        columns, display_columns = column_util.get_columns(obj, _attr_map)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if is_create:
        _get_attrs(client_manager, attrs, parsed_args)
    return attrs


def _get_attrs(client_manager, attrs, parsed_args):
    if parsed_args.protocol is not None:
        attrs['protocol'] = parsed_args.protocol
    if parsed_args.ethertype:
        attrs['ethertype'] = parsed_args.ethertype
    if parsed_args.source_ip_prefix is not None:
        attrs['source_ip_prefix'] = parsed_args.source_ip_prefix
    if parsed_args.destination_ip_prefix is not None:
        attrs['destination_ip_prefix'] = parsed_args.destination_ip_prefix
    if parsed_args.logical_source_port is not None:
        attrs['logical_source_port'] = _get_id(
            client_manager.neutronclient, parsed_args.logical_source_port,
            'port')
    if parsed_args.logical_destination_port is not None:
        attrs['logical_destination_port'] = _get_id(
            client_manager.neutronclient, parsed_args.logical_destination_port,
            'port')
    if parsed_args.source_port is not None:
        _fill_protocol_port_info(attrs, 'source',
                                        parsed_args.source_port)
    if parsed_args.destination_port is not None:
        _fill_protocol_port_info(attrs, 'destination',
                                        parsed_args.destination_port)
    if parsed_args.l7_parameters is not None:
        attrs['l7_parameters'] = parsed_args.l7_parameters


def _fill_protocol_port_info(attrs, port_type, port_val):
        min_port, sep, max_port = port_val.partition(":")
        if not min_port:
            msg = ("Invalid port value '%s', expected format is "
                   "min-port:max-port or min-port.")
            raise argparse.ArgumentTypeError(msg % port_val)
        if not max_port:
            max_port = min_port
        try:
            attrs[port_type + '_port_range_min'] = int(min_port)
            attrs[port_type + '_port_range_max'] = int(max_port)
        except ValueError:
            message = (_("Protocol port value %s must be an integer "
                         "or integer:integer.") % port_val)
            raise nc_exc.CommandError(message=message)


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, id_or_name)['id']
