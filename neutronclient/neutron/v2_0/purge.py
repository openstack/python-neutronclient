# Copyright 2016 Cisco Systems
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
import sys

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronV20


class Purge(neutronV20.NeutronCommand):
    """Delete all resources that belong to a given tenant."""

    def _pluralize(self, string):
        return string + 's'

    def _get_resources(self, neutron_client, resource_types, tenant_id):
        resources = []
        for resource_type in resource_types:
            resources.append([])
            resource_type_plural = self._pluralize(resource_type)
            opts = {'fields': ['id', 'tenant_id']}
            if resource_type_plural == 'ports':
                opts['fields'].append('device_id')
                opts['fields'].append('device_owner')
            function = getattr(neutron_client, 'list_%s' %
                               resource_type_plural)
            if callable(function):
                returned_resources = function(**opts).get(resource_type_plural,
                                                          [])
                for resource in returned_resources:
                    if resource['tenant_id'] == tenant_id:
                        index = resource_types.index(resource_type)
                        resources[index].append(resource)
                        self.total_resources += 1
        return resources

    def _delete_resource(self, neutron_client, resource_type, resource):
        resource_id = resource['id']
        if resource_type == 'port':
            router_interface_owners = ['network:router_interface',
                                       'network:router_interface_distributed']
            if resource.get('device_owner', '') in router_interface_owners:
                body = {'port_id': resource_id}
                neutron_client.remove_interface_router(resource['device_id'],
                                                       body)
                return
        function = getattr(neutron_client, 'delete_%s' % resource_type)
        if callable(function):
            function(resource_id)

    def _purge_resources(self, neutron_client, resource_types,
                         tenant_resources):
        deleted = {}
        failed = {}
        failures = False
        for resources in tenant_resources:
            index = tenant_resources.index(resources)
            resource_type = resource_types[index]
            failed[resource_type] = 0
            deleted[resource_type] = 0
            for resource in resources:
                try:
                    self._delete_resource(neutron_client, resource_type,
                                          resource)
                    deleted[resource_type] += 1
                    self.deleted_resources += 1
                except Exception:
                    failures = True
                    failed[resource_type] += 1
                    self.total_resources -= 1
                percent_complete = 100
                if self.total_resources > 0:
                    percent_complete = (self.deleted_resources /
                                        float(self.total_resources)) * 100
                sys.stdout.write("\rPurging resources: %d%% complete." %
                                 percent_complete)
                sys.stdout.flush()
        return (deleted, failed, failures)

    def _build_message(self, deleted, failed, failures):
        msg = ''
        deleted_msg = []
        for resource, value in deleted.items():
            if value:
                if not msg:
                    msg = 'Deleted'
                if not value == 1:
                    resource = self._pluralize(resource)
                deleted_msg.append(" %d %s" % (value, resource))
        if deleted_msg:
            msg += ','.join(deleted_msg)

        failed_msg = []
        if failures:
            if msg:
                msg += '. '
            msg += 'The following resources could not be deleted:'
            for resource, value in failed.items():
                if value:
                    if not value == 1:
                        resource = self._pluralize(resource)
                    failed_msg.append(" %d %s" % (value, resource))
            msg += ','.join(failed_msg)

        if msg:
            msg += '.'
        else:
            msg = _('Tenant has no supported resources.')

        return msg

    def get_parser(self, prog_name):
        parser = super(Purge, self).get_parser(prog_name)
        parser.add_argument(
            'tenant', metavar='TENANT',
            help=_('ID of Tenant owning the resources to be deleted.'))
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()

        self.any_failures = False

        # A list of the types of resources supported in the order in which
        # they should be deleted.
        resource_types = ['floatingip', 'port', 'router',
                          'network', 'security_group']

        deleted = {}
        failed = {}
        self.total_resources = 0
        self.deleted_resources = 0
        resources = self._get_resources(neutron_client, resource_types,
                                        parsed_args.tenant)
        deleted, failed, failures = self._purge_resources(neutron_client,
                                                          resource_types,
                                                          resources)
        print('\n%s' % self._build_message(deleted, failed, failures))
