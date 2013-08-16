# vim: tabstop=4 shiftwidth=4 softtabstop=4
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
#@author Abhishek Raut, Cisco Systems
#@author Sergey Sudakovich, Cisco Systems
#@author Rudrajit Tapadar, Cisco Systems

import logging

from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.neutron.v2_0 import parse_args_to_dict
from neutronclient.openstack.common.gettextutils import _

RESOURCE = 'network_profile'
SEGMENT_TYPE_CHOICES = ['vlan', 'vxlan', 'multi-segment', 'trunk']
SEGMENT_SUBTYPE_CHOICES = ['vlan', 'vxlan']


class ListNetworkProfile(neutronV20.ListCommand):
    """List network profiles that belong to a given tenant."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.ListNetworkProfile')
    _formatters = {}
    list_columns = ['id', 'name', 'segment_type', 'sub_type', 'segment_range',
                    'physical_network', 'multicast_ip_index',
                    'multicast_ip_range']


class ShowNetworkProfile(neutronV20.ShowCommand):
    """Show information of a given network profile."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.ShowNetworkProfile')
    allow_names = True


class CreateNetworkProfile(neutronV20.CreateCommand):
    """Creates a network profile."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.CreateNetworkProfile')

    def add_known_arguments(self, parser):
        parser.add_argument('name',
                            help='Name for Network Profile')
        parser.add_argument('segment_type',
                            choices=SEGMENT_TYPE_CHOICES,
                            help='Segment type')
        parser.add_argument('--sub_type',
                            choices=SEGMENT_SUBTYPE_CHOICES,
                            help='Sub-type for the Segment')
        parser.add_argument('--segment_range',
                            help='Range for the Segment')
        parser.add_argument('--physical_network',
                            help='Name for the Physical Network')
        parser.add_argument('--multicast_ip_range',
                            help='Multicast IPv4 Range')
        parser.add_argument("--add-tenant",
                            help="Add tenant to the network profile")

    def args2body(self, parsed_args):
        body = {'network_profile': {'name': parsed_args.name}}
        if parsed_args.segment_type:
            body['network_profile'].update({'segment_type':
                                           parsed_args.segment_type})
        if parsed_args.sub_type:
            body['network_profile'].update({'sub_type':
                                           parsed_args.sub_type})
        if parsed_args.segment_range:
            body['network_profile'].update({'segment_range':
                                           parsed_args.segment_range})
        if parsed_args.physical_network:
            body['network_profile'].update({'physical_network':
                                           parsed_args.physical_network})
        if parsed_args.multicast_ip_range:
            body['network_profile'].update({'multicast_ip_range':
                                           parsed_args.multicast_ip_range})
        if parsed_args.add_tenant:
            body['network_profile'].update({'add_tenant':
                                           parsed_args.add_tenant})
        return body


class DeleteNetworkProfile(neutronV20.DeleteCommand):
    """Delete a given network profile."""

    log = logging.getLogger(__name__ + '.DeleteNetworkProfile')
    resource = RESOURCE
    allow_names = True


class UpdateNetworkProfile(neutronV20.UpdateCommand):
    """Update network profile's information."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.UpdateNetworkProfile')


class UpdateNetworkProfileV2(neutronV20.NeutronCommand):

    api = 'network'
    log = logging.getLogger(__name__ + '.UpdateNetworkProfileV2')
    resource = RESOURCE

    def get_parser(self, prog_name):
        parser = super(UpdateNetworkProfileV2, self).get_parser(prog_name)
        parser.add_argument("--remove-tenant",
                            help="Remove tenant from the network profile")
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        data = {self.resource: parse_args_to_dict(parsed_args)}
        if parsed_args.remove_tenant:
            data[self.resource]['remove_tenant'] = parsed_args.remove_tenant
        neutron_client.update_network_profile(parsed_args.id,
                                              {self.resource: data})
        print >>self.app.stdout, (
            _('Updated %(resource)s: %(id)s') %
            {'id': parsed_args.id, 'resource': self.resource})
        return
