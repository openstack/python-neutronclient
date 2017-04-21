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

from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20

# key=object_type: value={key=resource, value=cmd_resource}
RBAC_OBJECTS = {'network': {'network': 'network'},
                'qos-policy': {'policy': 'qos_policy'}}


def _get_cmd_resource(obj_type):
    resource = list(RBAC_OBJECTS[obj_type])[0]
    cmd_resource = RBAC_OBJECTS[obj_type][resource]
    return resource, cmd_resource


def get_rbac_obj_params(client, obj_type, obj_id_or_name):
    resource, cmd_resource = _get_cmd_resource(obj_type)
    obj_id = neutronV20.find_resourceid_by_name_or_id(
        client=client, resource=resource, name_or_id=obj_id_or_name,
        cmd_resource=cmd_resource)

    return obj_id, cmd_resource


class ListRBACPolicy(neutronV20.ListCommand):
    """List RBAC policies that belong to a given tenant."""

    resource = 'rbac_policy'
    list_columns = ['id', 'object_type', 'object_id']
    pagination_support = True
    sorting_support = True
    allow_names = False


class ShowRBACPolicy(neutronV20.ShowCommand):
    """Show information of a given RBAC policy."""

    resource = 'rbac_policy'
    allow_names = False


class CreateRBACPolicy(neutronV20.CreateCommand):
    """Create a RBAC policy for a given tenant."""

    resource = 'rbac_policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='RBAC_OBJECT',
            help=_('ID or name of the RBAC object.'))
        parser.add_argument(
            '--type', choices=RBAC_OBJECTS.keys(),
            required=True,
            type=utils.convert_to_lowercase,
            help=_('Type of the object that RBAC policy affects.'))
        parser.add_argument(
            '--target-tenant',
            default='*',
            help=_('ID of the tenant to which the RBAC '
                   'policy will be enforced.'))
        parser.add_argument(
            '--action', choices=['access_as_external', 'access_as_shared'],
            type=utils.convert_to_lowercase,
            required=True,
            help=_('Action for the RBAC policy.'))

    def args2body(self, parsed_args):
        neutron_client = self.get_client()
        _object_id, _object_type = get_rbac_obj_params(neutron_client,
                                                       parsed_args.type,
                                                       parsed_args.name)
        body = {
            'object_id': _object_id,
            'object_type': _object_type,
            'target_tenant': parsed_args.target_tenant,
            'action': parsed_args.action,
        }
        return {self.resource: body}


class UpdateRBACPolicy(neutronV20.UpdateCommand):
    """Update RBAC policy for given tenant."""

    resource = 'rbac_policy'
    allow_names = False

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--target-tenant',
            help=_('ID of the tenant to which the RBAC '
                   'policy will be enforced.'))

    def args2body(self, parsed_args):
        body = {'target_tenant': parsed_args.target_tenant}
        return {self.resource: body}


class DeleteRBACPolicy(neutronV20.DeleteCommand):
    """Delete a RBAC policy."""

    resource = 'rbac_policy'
    allow_names = False
