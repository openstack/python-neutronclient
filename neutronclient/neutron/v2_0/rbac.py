# Copyright 2015 Huawei Technologies India Pvt Ltd.
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

from neutronclient.i18n import _
from neutronclient.neutron import v2_0 as neutronV20


def get_rbac_object_id(client, obj_type, obj_id_or_name):
    if obj_type == 'network':
        obj_id = neutronV20.find_resourceid_by_name_or_id(client,
                                                          'network',
                                                          obj_id_or_name)
    return obj_id


class ListRBACPolicy(neutronV20.ListCommand):
    """List RBAC policies that belong to a given tenant."""

    resource = 'rbac_policy'
    list_columns = ['id', 'object_id']
    pagination_support = True
    sorting_support = True


class ShowRBACPolicy(neutronV20.ShowCommand):
    """Show information of a given RBAC policy."""

    resource = 'rbac_policy'


class CreateRBACPolicy(neutronV20.CreateCommand):
    """Create a RBAC policy for a given tenant."""

    resource = 'rbac_policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='RBAC_OBJECT',
            help=_('ID or name of the RBAC object.'))
        parser.add_argument(
            '--type', choices=['network'],
            required=True,
            help=_('Type of the object that RBAC policy affects.'))
        parser.add_argument(
            '--target-tenant',
            help=_('ID of the tenant to which the RBAC '
                   'policy will be enforced.'))
        parser.add_argument(
            '--action', choices=['access_as_external', 'access_as_shared'],
            required=True,
            help=_('Action for the RBAC policy.'))

    def args2body(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _object_id = get_rbac_object_id(neutron_client, parsed_args.type,
                                        parsed_args.name)
        body = {self.resource: {
            'object_id': _object_id,
            'object_type': parsed_args.type,
            'target_tenant': parsed_args.target_tenant,
            'action': parsed_args.action,
        }, }
        return body


class UpdateRBACPolicy(neutronV20.UpdateCommand):
    """Update RBAC policy for given tenant."""

    resource = 'rbac_policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--target-tenant',
            help=_('ID of the tenant to which the RBAC '
                   'policy will be enforced.'))

    def args2body(self, parsed_args):

        body = {self.resource: {
            'target_tenant': parsed_args.target_tenant,
        }, }
        return body


class DeleteRBACPolicy(neutronV20.DeleteCommand):
    """Delete a RBAC policy."""

    resource = 'rbac_policy'
