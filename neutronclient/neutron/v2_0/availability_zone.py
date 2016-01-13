# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronv20


def add_az_hint_argument(parser, resource):
    parser.add_argument(
        '--availability-zone-hint', metavar='AVAILABILITY_ZONE',
        action='append', dest='availability_zone_hints',
        help=_('Availability Zone for the %s '
               '(requires availability zone extension, '
               'this option can be repeated).') % resource)


def args2body_az_hint(parsed_args, resource):
    if parsed_args.availability_zone_hints:
        resource['availability_zone_hints'] = (
            parsed_args.availability_zone_hints)


class ListAvailabilityZone(neutronv20.ListCommand):
    """List availability zones."""

    resource = 'availability_zone'
    list_columns = ['name', 'resource', 'state']
    pagination_support = True
    sorting_support = True
