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

from cliff import lister
from cliff import show

from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient import port_filters_v11_opt
from quantumclient.quantum.v1_1 import QuantumPortCommand


class ListPort(QuantumPortCommand, lister.Lister):
    """List ports that belong to a given tenant's network"""

    api = 'network'
    log = logging.getLogger(__name__ + '.ListPort')

    def get_parser(self, prog_name):
        parser = super(ListPort, self).get_parser(prog_name)

        parser.add_argument(
            '--show-details',
            help='show detailed info of networks',
            action='store_true',
            default=False, )
        for item in port_filters_v11_opt:
            option_key = item.keys()[0]
            option_defs = item.get(option_key)
            parser.add_argument(option_key, **option_defs)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        search_opts = {
            'tenant': parsed_args.tenant_id, }
        for item in port_filters_v11_opt:
            option_key = item.keys()[0]
            arg = option_key[2:]
            arg = arg.replace('-', '_')
            arg_value = getattr(parsed_args, arg, None)
            if arg_value is not None:
                search_opts.update({option_key[2:]: arg_value, })

        self.log.debug('search options: %s', search_opts)

        columns = ('ID', )
        data = None
        if parsed_args.show_details:
            data = quantum_client.list_ports_details(
                parsed_args.net_id, **search_opts)
            # dict:dict: {u'ports': [{
            #          u'op-status': u'DOWN',
            #          u'state': u'ACTIVE',
            #          u'id': u'479ba2b7-042f-44b9-aefb-b1550e114454'}, ]}
            columns = ('ID', 'op-status', 'state')
        else:
            data = quantum_client.list_ports(parsed_args.net_id, **search_opts)
            # {u'ports': [{u'id': u'7a068b68-c736-42ab-9e43-c9d83c57627e'}]}
        ports = []
        if 'ports' in data:
            ports = data['ports']

        return (columns,
                (utils.get_item_properties(
                    s, columns, formatters={}, ) for s in ports), )


class ShowPort(QuantumPortCommand, show.ShowOne):
    """Show information of a given port"""

    api = 'network'
    log = logging.getLogger(__name__ + '.ShowPort')

    def get_parser(self, prog_name):
        parser = super(ShowPort, self).get_parser(prog_name)
        parser.add_argument(
            'port_id', metavar='port-id',
            help='ID of the port to show', )
        parser.add_argument(
            '--show-details',
            help='show detailed info',
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
            data = quantum_client.show_port_details(
                parsed_args.net_id, parsed_args.port_id)
            # {u'port': {u'op-status': u'DOWN', u'state': u'ACTIVE',
            #            u'id': u'479ba2b7-042f-44b9-aefb-
            #  b1550e114454', u'attachment': {u'id': u'gw-7a068b68-c7'}}}
        else:
            data = quantum_client.show_port(
                parsed_args.net_id, parsed_args.port_id)
            # {u'port': {u'op-status': u'DOWN', u'state': u'ACTIVE',
            # u'id': u'479ba2b7-042f-44b9-aefb-b1550e114454'}}

        port = 'port' in data and data['port'] or None
        if port:
            attachment = 'attachment' in port and port['attachment'] or None
            if attachment:
                interface = attachment['id']
                port.update({'attachment': interface})
            return zip(*sorted(port.iteritems()))
        return ('', [])


class CreatePort(QuantumPortCommand, show.ShowOne):
    """Create port for a given network"""

    api = 'network'
    log = logging.getLogger(__name__ + '.CreatePort')

    def get_parser(self, prog_name):
        parser = super(CreatePort, self).get_parser(prog_name)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        data = quantum_client.create_port(parsed_args.net_id)
        # {u'network': {u'id': u'e9424a76-6db4-4c93-97b6-ec311cd51f19'}}
        info = 'port' in data and data['port'] or None
        if info:
            print >>self.app.stdout, _('Created a new Logical Port:')
        else:
            info = {'': ''}
        return zip(*sorted(info.iteritems()))


class DeletePort(QuantumPortCommand):
    """Delete a given port"""

    api = 'network'
    log = logging.getLogger(__name__ + '.DeletePort')

    def get_parser(self, prog_name):
        parser = super(DeletePort, self).get_parser(prog_name)
        parser.add_argument(
            'port_id', metavar='port-id',
            help='ID of the port to delete', )
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        quantum_client.delete_port(parsed_args.net_id, parsed_args.port_id)
        print >>self.app.stdout, (_('Deleted Logical Port: %(portid)s') %
                                  {'portid': parsed_args.port_id})
        return


class UpdatePort(QuantumPortCommand):
    """Update information of a given port"""

    api = 'network'
    log = logging.getLogger(__name__ + '.UpdatePort')

    def get_parser(self, prog_name):
        parser = super(UpdatePort, self).get_parser(prog_name)
        parser.add_argument(
            'port_id', metavar='port-id',
            help='ID of the port to update', )

        parser.add_argument(
            'newvalues', metavar='field=newvalue[,field2=newvalue2]',
            help='new values for the Port')

        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format
        field_values = parsed_args.newvalues
        data = {'port': {}}
        for kv in field_values.split(","):
            try:
                k, v = kv.split("=")
                data['port'][k] = v
            except ValueError:
                raise exceptions.CommandError(
                    "malformed new values (field=newvalue): %s" % kv)
        data['network_id'] = parsed_args.net_id
        data['port']['id'] = parsed_args.port_id

        quantum_client.update_port(
            parsed_args.net_id, parsed_args.port_id, data)
        print >>self.app.stdout, (_('Updated Logical Port: %(portid)s') %
                                  {'portid': parsed_args.port_id})
        return
