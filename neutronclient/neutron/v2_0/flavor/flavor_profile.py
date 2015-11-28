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


class ListFlavorProfile(neutronV20.ListCommand):
    """List Neutron service flavor profiles."""

    resource = 'service_profile'
    list_columns = ['id', 'description', 'enabled', 'metainfo']
    pagination_support = True
    sorting_support = True


class ShowFlavorProfile(neutronV20.ShowCommand):
    """Show information about a given Neutron service flavor profile."""

    resource = 'service_profile'


class CreateFlavorProfile(neutronV20.CreateCommand):
    """Create a Neutron service flavor profile."""

    resource = 'service_profile'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description for the flavor profile.'))
        parser.add_argument(
            '--driver',
            help=_('Python module path to driver.'))
        parser.add_argument(
            '--metainfo',
            help=_('Metainfo for the flavor profile.'))
        utils.add_boolean_argument(
            parser,
            '--enabled',
            default=argparse.SUPPRESS,
            help=_('Sets enabled flag.'))

    def args2body(self, parsed_args):
        body = {}
        neutronV20.update_dict(parsed_args, body,
                               ['description', 'driver', 'enabled',
                                'metainfo'])
        return {self.resource: body}


class DeleteFlavorProfile(neutronV20.DeleteCommand):
    """Delete a given Neutron service flavor profile."""

    resource = 'service_profile'


class UpdateFlavorProfile(neutronV20.UpdateCommand):
    """Update a given Neutron service flavor profile."""

    resource = 'service_profile'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description for the flavor profile.'))
        parser.add_argument(
            '--driver',
            help=_('Python module path to driver.'))
        parser.add_argument(
            '--metainfo',
            help=_('Metainfo for the flavor profile.'))
        utils.add_boolean_argument(
            parser,
            '--enabled',
            default=argparse.SUPPRESS,
            help=_('Sets enabled flag.'))

    def args2body(self, parsed_args):
        body = {}
        neutronV20.update_dict(parsed_args, body,
                               ['description', 'driver', 'enabled',
                                'metainfo'])
        return {self.resource: body}
