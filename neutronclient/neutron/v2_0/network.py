# Copyright 2012 OpenStack Foundation.
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

import argparse

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.neutron.v2_0 import availability_zone
from neutronclient.neutron.v2_0 import dns
from neutronclient.neutron.v2_0.qos import policy as qos_policy


def _format_subnets(network):
    try:
        return '\n'.join([' '.join([s['id'], s.get('cidr', '')])
                          for s in network['subnets']])
    except (TypeError, KeyError):
        return ''


def args2body_common(body, parsed_args):
    neutronV20.update_dict(parsed_args, body,
                           ['name', 'description'])


class ListNetwork(neutronV20.ListCommand):
    """List networks that belong to a given tenant."""

    # Length of a query filter on subnet id
    # id=<uuid>& (with len(uuid)=36)
    subnet_id_filter_len = 40
    resource = 'network'
    _formatters = {'subnets': _format_subnets, }
    list_columns = ['id', 'name', 'subnets']
    pagination_support = True
    sorting_support = True

    filter_attrs = [
        'tenant_id',
        'name',
        'admin_state_up',
        {'name': 'status',
         'help': _("Filter %s according to their operation status."
                   "(For example: ACTIVE, ERROR etc)"),
         'boolean': False,
         'argparse_kwargs': {'type': utils.convert_to_uppercase}},
        {'name': 'shared',
         'help': _('Filter and list the networks which are shared.'),
         'boolean': True},
        {'name': 'router:external',
         'help': _('Filter and list the networks which are external.'),
         'boolean': True},
        {'name': 'tags',
         'help': _("Filter and list %s which has all given tags. "
                   "Multiple tags can be set like --tags <tag[,tag...]>"),
         'boolean': False,
         'argparse_kwargs': {'metavar': 'TAG'}},
        {'name': 'tags_any',
         'help': _("Filter and list %s which has any given tags. "
                   "Multiple tags can be set like --tags-any <tag[,tag...]>"),
         'boolean': False,
         'argparse_kwargs': {'metavar': 'TAG'}},
        {'name': 'not_tags',
         'help': _("Filter and list %s which does not have all given tags. "
                   "Multiple tags can be set like --not-tags <tag[,tag...]>"),
         'boolean': False,
         'argparse_kwargs': {'metavar': 'TAG'}},
        {'name': 'not_tags_any',
         'help': _("Filter and list %s which does not have any given tags. "
                   "Multiple tags can be set like --not-tags-any "
                   "<tag[,tag...]>"),
         'boolean': False,
         'argparse_kwargs': {'metavar': 'TAG'}},
    ]

    def extend_list(self, data, parsed_args):
        """Add subnet information to a network list."""
        neutron_client = self.get_client()
        search_opts = {'fields': ['id', 'cidr']}
        if self.pagination_support:
            page_size = parsed_args.page_size
            if page_size:
                search_opts.update({'limit': page_size})
        subnet_ids = []
        for n in data:
            if 'subnets' in n:
                subnet_ids.extend(n['subnets'])

        def _get_subnet_list(sub_ids):
            search_opts['id'] = sub_ids
            return neutron_client.list_subnets(
                **search_opts).get('subnets', [])

        try:
            subnets = _get_subnet_list(subnet_ids)
        except exceptions.RequestURITooLong as uri_len_exc:
            # The URI is too long because of too many subnet_id filters
            # Use the excess attribute of the exception to know how many
            # subnet_id filters can be inserted into a single request
            subnet_count = len(subnet_ids)
            max_size = ((self.subnet_id_filter_len * subnet_count) -
                        uri_len_exc.excess)
            chunk_size = max_size // self.subnet_id_filter_len
            subnets = []
            for i in range(0, subnet_count, chunk_size):
                subnets.extend(
                    _get_subnet_list(subnet_ids[i: i + chunk_size]))

        subnet_dict = dict([(s['id'], s) for s in subnets])
        for n in data:
            if 'subnets' in n:
                n['subnets'] = [(subnet_dict.get(s) or {"id": s})
                                for s in n['subnets']]


class ListExternalNetwork(ListNetwork):
    """List external networks that belong to a given tenant."""

    pagination_support = True
    sorting_support = True

    def retrieve_list(self, parsed_args):
        external = '--router:external=True'
        if external not in self.values_specs:
            self.values_specs.append('--router:external=True')
        return super(ListExternalNetwork, self).retrieve_list(parsed_args)


class ShowNetwork(neutronV20.ShowCommand):
    """Show information of a given network."""

    resource = 'network'


class CreateNetwork(neutronV20.CreateCommand, qos_policy.CreateQosPolicyMixin):
    """Create a network for a given tenant."""

    resource = 'network'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false.'))
        parser.add_argument(
            '--admin_state_down',
            dest='admin_state', action='store_false',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--shared',
            action='store_true',
            help=_('Set the network as shared.'),
            default=argparse.SUPPRESS)
        parser.add_argument(
            '--provider:network_type',
            metavar='<network_type>',
            help=_('The physical mechanism by which the virtual network'
                   ' is implemented.'))
        parser.add_argument(
            '--provider:physical_network',
            metavar='<physical_network_name>',
            help=_('Name of the physical network over which the virtual '
                   'network is implemented.'))
        parser.add_argument(
            '--provider:segmentation_id',
            metavar='<segmentation_id>',
            help=_('VLAN ID for VLAN networks or tunnel-id for GRE/VXLAN '
                   'networks.'))
        utils.add_boolean_argument(
            parser,
            '--vlan-transparent',
            default=argparse.SUPPRESS,
            help=_('Create a VLAN transparent network.'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of the network to be created.'))
        parser.add_argument(
            '--description',
            help=_('Description of network.'))

        self.add_arguments_qos_policy(parser)
        availability_zone.add_az_hint_argument(parser, self.resource)
        dns.add_dns_argument_create(parser, self.resource, 'domain')

    def args2body(self, parsed_args):
        body = {'admin_state_up': parsed_args.admin_state}
        args2body_common(body, parsed_args)
        neutronV20.update_dict(parsed_args, body,
                               ['shared', 'tenant_id',
                                'vlan_transparent',
                                'provider:network_type',
                                'provider:physical_network',
                                'provider:segmentation_id',
                                'description'])
        self.args2body_qos_policy(parsed_args, body)
        availability_zone.args2body_az_hint(parsed_args, body)
        dns.args2body_dns_create(parsed_args, body, 'domain')
        return {'network': body}


class DeleteNetwork(neutronV20.DeleteCommand):
    """Delete a given network."""

    resource = 'network'


class UpdateNetwork(neutronV20.UpdateCommand, qos_policy.UpdateQosPolicyMixin):
    """Update network's information."""

    resource = 'network'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Name of the network.'))
        parser.add_argument(
            '--description',
            help=_('Description of this network.'))
        self.add_arguments_qos_policy(parser)
        dns.add_dns_argument_update(parser, self.resource, 'domain')

    def args2body(self, parsed_args):
        body = {}
        args2body_common(body, parsed_args)
        self.args2body_qos_policy(parsed_args, body)
        dns.args2body_dns_update(parsed_args, body, 'domain')
        return {'network': body}
