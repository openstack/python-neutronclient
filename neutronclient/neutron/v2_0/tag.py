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
from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronv20


# List of resources can be set tag
TAG_RESOURCES = ['network', 'subnet', 'port', 'router', 'subnetpool']


def _convert_resource_args(client, parsed_args):
    resource_type = client.get_resource_plural(parsed_args.resource_type)
    resource_id = neutronv20.find_resourceid_by_name_or_id(
        client, parsed_args.resource_type, parsed_args.resource)
    return resource_type, resource_id


def _add_common_arguments(parser):
    parser.add_argument('--resource-type',
                        choices=TAG_RESOURCES,
                        dest='resource_type',
                        required=True,
                        help=_('Resource Type.'))
    parser.add_argument('--resource',
                        required=True,
                        help=_('Resource name or ID.'))


class AddTag(neutronv20.NeutronCommand):
    """Add a tag into the resource."""

    def get_parser(self, prog_name):
        parser = super(AddTag, self).get_parser(prog_name)
        _add_common_arguments(parser)
        parser.add_argument('--tag',
                            required=True,
                            help=_('Tag to be added.'))
        return parser

    def take_action(self, parsed_args):
        client = self.get_client()
        if not parsed_args.tag:
            raise exceptions.CommandError(
                _('Cannot add an empty value as tag'))
        resource_type, resource_id = _convert_resource_args(client,
                                                            parsed_args)
        client.add_tag(resource_type, resource_id, parsed_args.tag)


class ReplaceTag(neutronv20.NeutronCommand):
    """Replace all tags on the resource."""

    def get_parser(self, prog_name):
        parser = super(ReplaceTag, self).get_parser(prog_name)
        _add_common_arguments(parser)
        parser.add_argument('--tag',
                            metavar='TAG',
                            action='append',
                            dest='tags',
                            required=True,
                            help=_('Tag (This option can be repeated).'))
        return parser

    def take_action(self, parsed_args):
        client = self.get_client()
        resource_type, resource_id = _convert_resource_args(client,
                                                            parsed_args)
        body = {'tags': parsed_args.tags}
        client.replace_tag(resource_type, resource_id, body)


class RemoveTag(neutronv20.NeutronCommand):
    """Remove a tag on the resource."""

    def get_parser(self, prog_name):
        parser = super(RemoveTag, self).get_parser(prog_name)
        _add_common_arguments(parser)
        tag_opt = parser.add_mutually_exclusive_group()
        tag_opt.add_argument('--all',
                             action='store_true',
                             help=_('Remove all tags on the resource.'))
        tag_opt.add_argument('--tag',
                             help=_('Tag to be removed.'))
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.all and not parsed_args.tag:
            raise exceptions.CommandError(
                _("--all or --tag must be specified"))
        client = self.get_client()
        resource_type, resource_id = _convert_resource_args(client,
                                                            parsed_args)
        if parsed_args.all:
            client.remove_tag_all(resource_type, resource_id)
        else:
            client.remove_tag(resource_type, resource_id, parsed_args.tag)
