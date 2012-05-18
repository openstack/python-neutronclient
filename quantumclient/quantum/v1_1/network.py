# Copyright 2012 OpenStack LLC.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging
import itertools

from cliff import lister
from cliff import show

from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient import net_filters_v11_opt
from quantumclient.quantum.v1_1 import QuantumCommand


class ListNetwork(QuantumCommand, lister.Lister):
    """List networks that belong to a given tenant"""

    api = 'network'
    log = logging.getLogger(__name__ + '.ListNetwork')

    def get_parser(self, prog_name):
        parser = super(ListNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--show-details',
            help='show detailed info',
            action='store_true',
            default=False, )
        for net_filter in net_filters_v11_opt:
            option_key = net_filter.keys()[0]
            option_defs = net_filter.get(option_key)
            parser.add_argument(option_key, **option_defs)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        search_opts = {
            'tenant': parsed_args.tenant_id, }
        for net_filter in net_filters_v11_opt:
            option_key = net_filter.keys()[0]
            arg = option_key[2:]
            arg = arg.replace('-', '_')
            arg_value = getattr(parsed_args, arg, None)
            if arg_value is not None:
                search_opts.update({option_key[2:]: arg_value, })

        self.log.debug('search options: %s', search_opts)
        quantum_client.format = parsed_args.request_format
        columns = ('ID', )
        data = None
        if parsed_args.show_details:
            data = quantum_client.list_networks_details(**search_opts)
            # dict: {u'networks': [{u'op-status': u'UP',
            #        u'id': u'7a068b68-c736-42ab-9e43-c9d83c57627e',
            #        u'name': u'private'}]}
            columns = ('ID', 'op-status', 'name', )
        else:
            data = quantum_client.list_networks(**search_opts)
            # {u'networks': [{u'id':
            #  u'7a068b68-c736-42ab-9e43-c9d83c57627e'}]}
        networks = []
        if 'networks' in data:
            networks = data['networks']

        return (columns,
                (utils.get_item_properties(
                    s, columns, formatters={}, ) for s in networks), )


def _format_attachment(port):
    # attachment {u'id': u'gw-7a068b68-c7'}
    try:
        return ('attachment' in port and port['attachment'] and
                'id' in port['attachment'] and
                port['attachment']['id'] or '')
    except Exception:
        return ''


class ShowNetwork(QuantumCommand, show.ShowOne):
    """Show information of a given network"""

    api = 'network'
    log = logging.getLogger(__name__ + '.ShowNetwork')

    def get_parser(self, prog_name):
        parser = super(ShowNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'net_id', metavar='net-id',
            help='ID of network to display')

        parser.add_argument(
            '--show-details',
            help='show detailed info of networks',
            action='store_true',
            default=False, )
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        data = None
        if parsed_args.show_details:
            data = quantum_client.show_network_details(parsed_args.net_id)
        else:
            data = quantum_client.show_network(parsed_args.net_id)
        # {u'network': {u'op-status': u'UP', 'xmlns':
        #               u'http://openstack.org/quantum/api/v1.1', u'id':
        # u'7a068b68-c736-42ab-9e43-c9d83c57627e', u'name': u'private'}}
        network = {}
        ports = None
        network = 'network' in data and data['network'] or None
        if network:
            ports = network.pop('ports', None)
            column_names, data = zip(*sorted(network.iteritems()))
            if not parsed_args.columns:
                columns_to_include = column_names
            else:
                columns_to_include = [c for c in column_names
                                      if c in parsed_args.columns]
                # Set up argument to compress()
                selector = [(c in columns_to_include)
                            for c in column_names]
                data = list(itertools.compress(data, selector))
            formatter = self.formatters[parsed_args.formatter]
            formatter.emit_one(columns_to_include, data,
                               self.app.stdout, parsed_args)
        if ports:
            print >>self.app.stdout, _('Network Ports:')
            columns = ('op-status', 'state', 'id', 'attachment', )
            column_names, data = (columns, (utils.get_item_properties(
                s, columns, formatters={'attachment': _format_attachment}, )
                for s in ports), )
            if not parsed_args.columns:
                columns_to_include = column_names
                data_gen = data
            else:
                columns_to_include = [c for c in column_names
                                      if c in parsed_args.columns]
                if not columns_to_include:
                    raise ValueError(
                        'No recognized column names in %s' %
                        str(parsed_args.columns))
                # Set up argument to compress()
                selector = [(c in columns_to_include)
                            for c in column_names]
                # Generator expression to only return the parts of a row
                # of data that the user has expressed interest in
                # seeing. We have to convert the compress() output to a
                # list so the table formatter can ask for its length.
                data_gen = (list(itertools.compress(row, selector))
                            for row in data)
            formatter = self.formatters[parsed_args.formatter]
            formatter.emit_list(columns_to_include,
                                data_gen, self.app.stdout, parsed_args)

        return ('', [])


class CreateNetwork(QuantumCommand, show.ShowOne):
    """Create a network for a given tenant"""

    api = 'network'
    log = logging.getLogger(__name__ + '.CreateNetwork')

    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'net_name', metavar='net-name',
            help='Name of network to create')

        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        body = {'network': {'name': parsed_args.net_name, }, }
        network = quantum_client.create_network(body)
        # {u'network': {u'id': u'e9424a76-6db4-4c93-97b6-ec311cd51f19'}}
        info = 'network' in network and network['network'] or None
        if info:
            print >>self.app.stdout, _('Created a new Virtual Network:')
        else:
            info = {'': ''}
        return zip(*sorted(info.iteritems()))


class DeleteNetwork(QuantumCommand):
    """Delete a given network"""

    api = 'network'
    log = logging.getLogger(__name__ + '.DeleteNetwork')

    def get_parser(self, prog_name):
        parser = super(DeleteNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'net_id', metavar='net-id',
            help='ID of network to delete')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        quantum_client.delete_network(parsed_args.net_id)
        print >>self.app.stdout, (_('Deleted Network: %(networkid)s')
                                  % {'networkid': parsed_args.net_id})
        return


class UpdateNetwork(QuantumCommand):
    """Update network's information"""

    api = 'network'
    log = logging.getLogger(__name__ + '.UpdateNetwork')

    def get_parser(self, prog_name):
        parser = super(UpdateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'net_id', metavar='net-id',
            help='ID of network to update')

        parser.add_argument(
            'newvalues', metavar='field=newvalue[,field2=newvalue2]',
            help='new values for the network')
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        field_values = parsed_args.newvalues
        data = {'network': {}}
        for kv in field_values.split(","):
            try:
                k, v = kv.split("=")
                data['network'][k] = v
            except ValueError:
                raise exceptions.CommandError(
                    "malformed new values (field=newvalue): %s" % kv)

        data['network']['id'] = parsed_args.net_id
        quantum_client.update_network(parsed_args.net_id, data)
        print >>self.app.stdout, (
            _('Updated Network: %(networkid)s') %
            {'networkid': parsed_args.net_id})
        return
