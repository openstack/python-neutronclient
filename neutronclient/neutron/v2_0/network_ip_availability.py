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

from cliff import show

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronV20


class ListIpAvailability(neutronV20.ListCommand):
    """List IP usage of networks"""

    resource = 'network_ip_availability'
    resource_plural = 'network_ip_availabilities'
    list_columns = ['network_id', 'network_name', 'total_ips', 'used_ips']
    paginations_support = True
    sorting_support = True

    filter_attrs = [
        {'name': 'ip_version',
         'help': _('Returns IP availability for the network subnets '
                   'with a given IP version. Default: 4'),
         'argparse_kwargs': {'type': int,
                             'choices': [4, 6],
                             'default': 4}
         },
        {'name': 'network_id',
         'help': _('Returns IP availability for the network '
                   'matching a given network ID.')},
        {'name': 'network_name',
         'help': _('Returns IP availability for the network '
                   'matching a given name.')},
        {'name': 'tenant_id',
         'help': _('Returns IP availability for the networks '
                   'with a given tenant ID.')},
    ]


class ShowIpAvailability(neutronV20.NeutronCommand, show.ShowOne):
    """Show IP usage of specific network"""

    resource = 'network_ip_availability'

    def get_parser(self, prog_name):
        parser = super(ShowIpAvailability, self).get_parser(prog_name)
        parser.add_argument(
            'network_id', metavar='NETWORK',
            help=_('ID or name of network to look up.'))
        return parser

    def take_action(self, parsed_args):
        self.log.debug('run(%s)', parsed_args)
        neutron_client = self.get_client()
        _id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'network', parsed_args.network_id)
        data = neutron_client.show_network_ip_availability(_id)
        self.format_output_data(data)
        resource = data[self.resource]
        if self.resource in data:
            return zip(*sorted(resource.items()))
        else:
            return None
