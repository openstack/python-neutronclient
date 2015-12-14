# Copyright 2015 Huawei Technologies India Pvt Ltd, Inc.
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

import os

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronv20


def get_qos_policy_id(client, policy_id_or_name):
    _policy_id = neutronv20.find_resourceid_by_name_or_id(
        client, 'policy', policy_id_or_name, cmd_resource='qos_policy')
    return _policy_id


class CreateQosPolicyMixin(object):
    def add_arguments_qos_policy(self, parser):
        qos_policy_args = parser.add_mutually_exclusive_group()
        qos_policy_args.add_argument(
            '--qos-policy',
            help=_('ID or name of the QoS policy that should'
                   'be attached to the resource.'))
        return qos_policy_args

    def args2body_qos_policy(self, parsed_args, resource):
        if parsed_args.qos_policy:
            _policy_id = get_qos_policy_id(self.get_client(),
                                           parsed_args.qos_policy)
            resource['qos_policy_id'] = _policy_id


class UpdateQosPolicyMixin(CreateQosPolicyMixin):
    def add_arguments_qos_policy(self, parser):
        qos_policy_args = (super(UpdateQosPolicyMixin, self).
                           add_arguments_qos_policy(parser))
        qos_policy_args.add_argument(
            '--no-qos-policy',
            action='store_true',
            help=_('Detach QoS policy from the resource.'))
        return qos_policy_args

    def args2body_qos_policy(self, parsed_args, resource):
        super(UpdateQosPolicyMixin, self).args2body_qos_policy(parsed_args,
                                                               resource)
        if parsed_args.no_qos_policy:
            resource['qos_policy_id'] = None


class ListQoSPolicy(neutronv20.ListCommand):
    """List QoS policies that belong to a given tenant connection."""

    resource = 'policy'
    shadow_resource = 'qos_policy'
    list_columns = ['id', 'name']
    pagination_support = True
    sorting_support = True


class ShowQoSPolicy(neutronv20.ShowCommand):
    """Show information of a given qos policy."""

    resource = 'policy'
    shadow_resource = 'qos_policy'

    def format_output_data(self, data):
        rules = []
        for rule in data['policy'].get('rules', []):
            rules.append("%s (type: %s)" % (rule['id'], rule['type']))
        data['policy']['rules'] = os.linesep.join(rules)

        super(ShowQoSPolicy, self).format_output_data(data)


class CreateQoSPolicy(neutronv20.CreateCommand):
    """Create a qos policy."""

    resource = 'policy'
    shadow_resource = 'qos_policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of the QoS policy to be created.'))
        parser.add_argument(
            '--description',
            help=_('Description of the QoS policy to be created.'))
        parser.add_argument(
            '--shared',
            action='store_true',
            help=_('Accessible by other tenants. '
                   'Set shared to True (default is False).'))

    def args2body(self, parsed_args):
        body = {'name': parsed_args.name}
        if parsed_args.description:
            body['description'] = parsed_args.description
        if parsed_args.shared:
            body['shared'] = parsed_args.shared
        if parsed_args.tenant_id:
            body['tenant_id'] = parsed_args.tenant_id
        return {self.resource: body}


class UpdateQoSPolicy(neutronv20.UpdateCommand):
    """Update a given qos policy."""

    resource = 'policy'
    shadow_resource = 'qos_policy'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Name of the QoS policy.'))
        parser.add_argument(
            '--description',
            help=_('Description of the QoS policy.'))
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--shared',
            action='store_true',
            help=_('Accessible by other tenants. '
                   'Set shared to True (default is False).'))
        shared_group.add_argument(
            '--no-shared',
            action='store_true',
            help=_('Not accessible by other tenants. '
                   'Set shared to False.'))

    def args2body(self, parsed_args):
        body = {}
        if parsed_args.name:
            body['name'] = parsed_args.name
        if parsed_args.description:
            body['description'] = parsed_args.description
        if parsed_args.shared:
            body['shared'] = True
        if parsed_args.no_shared:
            body['shared'] = False

        return {self.resource: body}


class DeleteQoSPolicy(neutronv20.DeleteCommand):
    """Delete a given qos policy."""

    resource = 'policy'
    shadow_resource = 'qos_policy'
