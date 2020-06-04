# Copyright 2016 IBM
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

from cliff import show
from oslo_serialization import jsonutils

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.neutron import v2_0


class ShowAutoAllocatedTopology(v2_0.NeutronCommand, show.ShowOne):
    """Show the auto-allocated topology of a given tenant."""

    resource = 'auto_allocated_topology'

    def get_parser(self, prog_name):
        parser = super(ShowAutoAllocatedTopology, self).get_parser(prog_name)
        parser.add_argument(
            '--dry-run',
            help=_('Validate the requirements for auto-allocated-topology. '
                   '(Does not return a topology.)'),
            action='store_true')
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID.'))
        # Allow people to do
        #    neutron auto-allocated-topology-show <tenant-id>
        # (Only useful to users who can look at other tenants' topologies.)
        # We use a different name for this arg because the default will
        # override whatever is in the named arg otherwise.
        parser.add_argument(
            'pos_tenant_id',
            help=argparse.SUPPRESS, nargs='?')
        return parser

    def take_action(self, parsed_args):
        client = self.get_client()
        extra_values = v2_0.parse_args_to_dict(self.values_specs)
        if extra_values:
            raise exceptions.CommandError(
                _("Invalid argument(s): --%s") % ', --'.join(extra_values))
        tenant_id = parsed_args.tenant_id or parsed_args.pos_tenant_id
        if parsed_args.dry_run:
            data = client.validate_auto_allocated_topology_requirements(
                tenant_id)
        else:
            data = client.get_auto_allocated_topology(tenant_id)
        if self.resource in data:
            for k, v in data[self.resource].items():
                if isinstance(v, list):
                    value = ""
                    for _item in v:
                        if value:
                            value += "\n"
                        if isinstance(_item, dict):
                            value += jsonutils.dumps(_item)
                        else:
                            value += str(_item)
                    data[self.resource][k] = value
                elif v == "dry-run=pass":
                    return ("dry-run",), ("pass",)
                elif v is None:
                    data[self.resource][k] = ''
            return zip(*sorted(data[self.resource].items()))
        else:
            return None


class DeleteAutoAllocatedTopology(v2_0.NeutronCommand):
    """Delete the auto-allocated topology of a given tenant."""

    resource = 'auto_allocated_topology'

    def get_parser(self, prog_name):
        parser = super(DeleteAutoAllocatedTopology, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID.'))
        # Allow people to do
        #    neutron auto-allocated-topology-delete <tenant-id>
        # (Only useful to users who can look at other tenants' topologies.)
        # We use a different name for this arg because the default will
        # override whatever is in the named arg otherwise.
        parser.add_argument(
            'pos_tenant_id',
            help=argparse.SUPPRESS, nargs='?')
        return parser

    def take_action(self, parsed_args):
        client = self.get_client()
        tenant_id = parsed_args.tenant_id or parsed_args.pos_tenant_id
        client.delete_auto_allocated_topology(tenant_id)
        # It tenant is None, let's be clear on what it means.
        tenant_id = tenant_id or 'None (i.e. yours)'
        print(_('Deleted topology for tenant %s.') % tenant_id,
              file=self.app.stdout)
