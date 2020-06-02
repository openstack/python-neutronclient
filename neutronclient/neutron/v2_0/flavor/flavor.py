# Copyright 2015 Hewlett-Packard Development Company, L.P.
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

import argparse

from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


class ListFlavor(neutronV20.ListCommand):
    """List Neutron service flavors."""

    resource = 'flavor'
    list_columns = ['id', 'name', 'service_type', 'enabled']
    pagination_support = True
    sorting_support = True


class ShowFlavor(neutronV20.ShowCommand):
    """Show information about a given Neutron service flavor."""

    resource = 'flavor'


class CreateFlavor(neutronV20.CreateCommand):
    """Create a Neutron service flavor."""

    resource = 'flavor'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='NAME',
            help=_('Name for the flavor.'))
        parser.add_argument(
            'service_type',
            metavar='SERVICE_TYPE',
            help=_('Service type to which the flavor applies to: e.g. VPN. '
                   '(See service-provider-list for loaded examples.)'))
        parser.add_argument(
            '--description',
            help=_('Description for the flavor.'))
        utils.add_boolean_argument(
            parser,
            '--enabled',
            default=argparse.SUPPRESS,
            help=_('Sets enabled flag.'))

    def args2body(self, parsed_args):
        body = {}
        neutronV20.update_dict(parsed_args, body,
                               ['name', 'description', 'service_type',
                                'enabled'])
        return {self.resource: body}


class DeleteFlavor(neutronV20.DeleteCommand):
    """Delete a given Neutron service flavor."""

    resource = 'flavor'


class UpdateFlavor(neutronV20.UpdateCommand):
    """Update a Neutron service flavor."""

    resource = 'flavor'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Name for the flavor.'))
        parser.add_argument(
            '--description',
            help=_('Description for the flavor.'))
        utils.add_boolean_argument(
            parser,
            '--enabled',
            default=argparse.SUPPRESS,
            help=_('Sets enabled flag.'))

    def args2body(self, parsed_args):
        body = {}
        neutronV20.update_dict(parsed_args, body,
                               ['name', 'description', 'enabled'])
        return {self.resource: body}


class AssociateFlavor(neutronV20.NeutronCommand):
    """Associate a Neutron service flavor with a flavor profile."""

    resource = 'flavor'

    def get_parser(self, prog_name):
        parser = super(AssociateFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='FLAVOR',
            help=_('ID or name of the flavor to associate.'))
        parser.add_argument(
            'flavor_profile',
            metavar='FLAVOR_PROFILE',
            help=_('ID of the flavor profile to be associated with the '
                   'flavor.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        flavor_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'flavor', parsed_args.flavor)
        service_profile_id = neutronV20.find_resourceid_by_id(
            neutron_client, 'service_profile', parsed_args.flavor_profile)
        body = {'service_profile': {'id': service_profile_id}}
        neutron_client.associate_flavor(flavor_id, body)
        print((_('Associated flavor %(flavor)s with '
                 'flavor_profile %(profile)s') %
               {'flavor': parsed_args.flavor,
                'profile': parsed_args.flavor_profile}),
              file=self.app.stdout)


class DisassociateFlavor(neutronV20.NeutronCommand):
    """Disassociate a Neutron service flavor from a flavor profile."""

    resource = 'flavor'

    def get_parser(self, prog_name):
        parser = super(DisassociateFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='FLAVOR',
            help=_('ID or name of the flavor to be disassociated.'))
        parser.add_argument(
            'flavor_profile',
            metavar='FLAVOR_PROFILE',
            help=_('ID of the flavor profile to be disassociated from the '
                   'flavor.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        flavor_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'flavor', parsed_args.flavor)
        service_profile_id = neutronV20.find_resourceid_by_id(
            neutron_client, 'service_profile', parsed_args.flavor_profile)
        neutron_client.disassociate_flavor(flavor_id, service_profile_id)
        print((_('Disassociated flavor %(flavor)s from '
                 'flavor_profile %(profile)s') %
               {'flavor': parsed_args.flavor,
                'profile': parsed_args.flavor_profile}),
              file=self.app.stdout)
