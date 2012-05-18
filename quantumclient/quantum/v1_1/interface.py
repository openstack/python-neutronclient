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

from cliff import show

from quantumclient.quantum.v1_1 import QuantumInterfaceCommand


class PlugInterface(QuantumInterfaceCommand):
    """Plug interface to a given port"""

    api = 'network'
    log = logging.getLogger(__name__ + '.PlugInterface')

    def get_parser(self, prog_name):
        parser = super(PlugInterface, self).get_parser(prog_name)
        parser.add_argument(
            'iface_id', metavar='iface-id',
            help='_(ID of the interface to plug)', )
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format

        data = {'attachment': {'id': '%s' % parsed_args.iface_id, }, }
        quantum_client.attach_resource(parsed_args.net_id,
                                       parsed_args.port_id,
                                       data)
        print >>self.app.stdout, (_('Plugged interface %(interfaceid)s'
                                    ' into Logical Port %(portid)s')
                                  % {'interfaceid': parsed_args.iface_id,
                                     'portid': parsed_args.port_id, })

        return


class UnPlugInterface(QuantumInterfaceCommand):
    """Unplug interface from a given port"""

    api = 'network'
    log = logging.getLogger(__name__ + '.UnPlugInterface')

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format

        quantum_client.detach_resource(parsed_args.net_id, parsed_args.port_id)
        print >>self.app.stdout, (
            _('Unplugged interface on Logical Port %(portid)s')
            % {'portid': parsed_args.port_id, })

        return


class ShowInterface(QuantumInterfaceCommand, show.ShowOne):
    """Show interface on a given port"""

    api = 'network'
    log = logging.getLogger(__name__ + '.ShowInterface')

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.app.client_manager.quantum
        quantum_client.tenant = parsed_args.tenant_id
        quantum_client.format = parsed_args.request_format

        iface = quantum_client.show_port_attachment(
            parsed_args.net_id,
            parsed_args.port_id)['attachment']

        if iface:
            if 'id' not in iface:
                iface['id'] = '<none>'
        else:
            iface = {'': ''}
        return zip(*sorted(iface.iteritems()))
