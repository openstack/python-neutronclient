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

import logging
import string

from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


class ListEndpoint(neutronV20.ListCommand):
    """List endpoints that belong to a given tenant."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.ListEndpoint')
    _formatters = {}
    list_columns = ['id', 'name', 'description']
    pagination_support = True
    sorting_support = True


class ShowEndpoint(neutronV20.ShowCommand):
    """Show information of a given endpoint."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.ShowEndpoint')


class UpdateEndpointPortMixin(object):
    def add_arguments_port(self, parser):
        parser.add_argument(
            '--port',
            default='',
            help=_('Port uuid'))

    def args2body_port(self, parsed_args, endpoint):
        if parsed_args.port:
            endpoint['port'] = neutronV20_find_resourceid_by_name_or_id(
                self.get_client(), 'port', parsed_args.port)


class CreateEndpoint(neutronV20.CreateCommand, UpdateEndpointPortMixin):
    """Create a endpoint for a given tenant."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.CreateEndpoint')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the endpoint'))
        parser.add_argument(
            '--endpoint-group', metavar='EPG',
            default='',
            help=_('endpoint_group uuid'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of endpoint to create'))

        self.add_arguments_port(parser)

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description'])
        if parsed_args.endpoint_group:
            body[self.resource]['endpoint_group_id'] = \
                neutronV20_find_resourceid_by_name_or_id(
                    self.get_client(), 'endpoint_group',
                    parsed_args.endpoint_group)

        self.args2body_port(parsed_args, body[self.resource])

        return body


class DeleteEndpoint(neutronV20.DeleteCommand):
    """Delete a given endpoint."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.DeleteEndpoint')


class UpdateEndpoint(neutronV20.UpdateCommand):
    """Update endpoint's information."""

    resource = 'endpoint'
    log = logging.getLogger(__name__ + '.UpdateEndpoint')


def _format_endpoints(endpoint_group):
    out = '\n'.join([endpoint for endpoint in endpoint_group['endpoints']])
    return out


class ListEndpointGroup(neutronV20.ListCommand):
    """List endpoint_groups that belong to a given tenant."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.ListEndpointGroup')
    list_columns = ['id', 'name', 'description', 'parent_id',
                    'endpoints']
    _formatters = {'endpoints': _format_endpoints, }
    pagination_support = True
    sorting_support = True


class ShowEndpointGroup(neutronV20.ShowCommand):
    """Show information of a given endpoint_group."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.ShowEndpointGroup')


class UpdateEndpointGroupSubnetMixin(object):
    def add_arguments_subnet(self, parser):
        parser.add_argument(
            '--subnet',
            default='',
            help=_('Subnet uuid'))

    def args2body_subnet(self, parsed_args, endpoint):
        if parsed_args.subnet:
            endpoint['subnet'] = neutronV20_find_resourceid_by_name_or_id(
                self.get_client(), 'subnet', parsed_args.subnet)


class CreateEndpointGroup(neutronV20.CreateCommand,
                          UpdateEndpointGroupSubnetMixin):
    """Create a endpoint_group for a given tenant."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.CreateEndpointGroup')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the endpoint_group'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of endpoint_group to create'))
        parser.add_argument(
            '--parent_id', metavar='PARENT EPG',
            help=_('Parent endpoint_group uuid'))
        parser.add_argument(
            '--endpoints', type=string.split,
            default=[],
            help=_('Parent endpoint_group uuid'))
        parser.add_argument(
            '--bridge-domain', metavar='BRIDGE DOMAIN',
            default='',
            help=_('Bridge domain uuid'))
        parser.add_argument(
            '--provided_contract_scopes', type=string.split,
            default=[],
            help=_('Parent endpoint_group uuid'))
        parser.add_argument(
            '--consumed_contract_scopes', type=string.split,
            default=[],
            help=_('Parent endpoint_group uuid'))

        self.add_arguments_subnet(parser)

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        attr_map = {'endpoints': 'endpoint',
                    'provided_contract_scopes': 'contract_scope',
                    'consumed_contract_scopes': 'contract_scope'}
        for attr_name, res_name in attr_map.items():
            if getattr(parsed_args, attr_name):
                _uuids = [
                    neutronV20_find_resourceid_by_name_or_id(
                        self.get_client(),
                        res_name,
                        elem) for elem in getattr(parsed_args, attr_name)]
                body[self.resource][attr_name] = _uuids

        if parsed_args.bridge_domain:
            body[self.resource]['bridge_domain_id'] = \
                neutronV20_find_resourceid_by_name_or_id(
                    self.get_client(), 'bridge_domain',
                    parsed_args.bridge_domain)

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description',
                                'parent_id'])

        self.args2body_subnet(parsed_args, body[self.resource])

        return body


class DeleteEndpointGroup(neutronV20.DeleteCommand):
    """Delete a given endpoint_group."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.DeleteEndpointGroup')


class UpdateEndpointGroup(neutronV20.UpdateCommand):
    """Update endpoint_group's information."""

    resource = 'endpoint_group'
    log = logging.getLogger(__name__ + '.UpdateEndpointGroup')


class ListContract(neutronV20.ListCommand):
    """List contracts that belong to a given tenant."""

    resource = 'contract'
    log = logging.getLogger(__name__ + '.ListContract')
    _formatters = {}
    list_columns = ['id', 'name', 'description', 'ploicy_rules']
    pagination_support = True
    sorting_support = True


class ShowContract(neutronV20.ShowCommand):
    """Show information of a given contract."""

    resource = 'contract'
    log = logging.getLogger(__name__ + '.ShowContract')


class CreateContract(neutronV20.CreateCommand):
    """Create a contract for a given tenant."""

    resource = 'contract'
    log = logging.getLogger(__name__ + '.CreateContract')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the contract'))
        parser.add_argument(
            '--policy-rules', type=string.split,
            #default=[],
            help=_('list of policy rules'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of contract to create'))

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        if parsed_args.policy_rules:
            body[self.resource]['policy_rules'] = [
                neutronV20_find_resourceid_by_name_or_id(
                    self.get_client(),
                    'policy_rule',
                    elem) for elem in parsed_args.policy_rules]

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description'])

        return body


class DeleteContract(neutronV20.DeleteCommand):
    """Delete a given contract."""

    resource = 'contract'
    log = logging.getLogger(__name__ + '.DeleteContract')


class UpdateContract(neutronV20.UpdateCommand):
    """Update contract's information."""

    resource = 'contract'
    log = logging.getLogger(__name__ + '.UpdateContract')


class ListPolicyRule(neutronV20.ListCommand):
    """List policy_rules that belong to a given tenant."""

    resource = 'policy_rule'
    log = logging.getLogger(__name__ + '.ListPolicyRule')
    _formatters = {}
    list_columns = ['id', 'name', 'description', 'enabled', 'classifier_id',
                    'actions']
    pagination_support = True
    sorting_support = True


class ShowPolicyRule(neutronV20.ShowCommand):
    """Show information of a given policy_rule."""

    resource = 'policy_rule'
    log = logging.getLogger(__name__ + '.ShowPolicyRule')


class CreatePolicyRule(neutronV20.CreateCommand):
    """Create a policy_rule for a given tenant."""

    resource = 'policy_rule'
    log = logging.getLogger(__name__ + '.CreatePolicyRule')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the policy_rule'))
        parser.add_argument(
            '--enabled', type=bool,
            help=_('Enable flag'))
        parser.add_argument(
            '--classifier-id',
            help=_('uuid of classifier'))
        parser.add_argument(
            '--actions', type=string.split,
            #default=[],
            help=_('list of actions'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of policy_rule to create'))

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        if parsed_args.actions:
            body[self.resource]['actions'] = [
                neutronV20_find_resourceid_by_name_or_id(
                    self.get_client(),
                    'action',
                    elem) for elem in parsed_args.actions]

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description',
                                'enabled', 'classifier_id'])

        return body


class DeletePolicyRule(neutronV20.DeleteCommand):
    """Delete a given policy_rule."""

    resource = 'policy_rule'
    log = logging.getLogger(__name__ + '.DeletePolicyRule')


class UpdatePolicyRule(neutronV20.UpdateCommand):
    """Update policy_rule's information."""

    resource = 'policy_rule'
    log = logging.getLogger(__name__ + '.UpdatePolicyRule')


class ListClassifier(neutronV20.ListCommand):
    """List classifiers that belong to a given tenant."""

    resource = 'classifier'
    log = logging.getLogger(__name__ + '.ListClassifier')
    _formatters = {}
    list_columns = ['id', 'name', 'description', 'protocol', 'port_range',
                    'direction']
    pagination_support = True
    sorting_support = True


class ShowClassifier(neutronV20.ShowCommand):
    """Show information of a given classifier."""

    resource = 'classifier'
    log = logging.getLogger(__name__ + '.ShowClassifier')


class CreateClassifier(neutronV20.CreateCommand):
    """Create a classifier for a given tenant."""

    resource = 'classifier'
    log = logging.getLogger(__name__ + '.CreateClassifier')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the classifier'))
        parser.add_argument(
            '--protocol',
            choices=['tcp', 'udp', 'icmp'],
            help=_('Protocol'))
        parser.add_argument(
            '--port-range',
            help=_('Port range'))
        parser.add_argument(
            '--direction',
            choices=['in', 'out', 'bi'],
            help=_('Direction'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of classifier to create'))

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description',
                                'protocol', 'port_range', 'direction'])

        return body


class DeleteClassifier(neutronV20.DeleteCommand):
    """Delete a given classifier."""

    resource = 'classifier'
    log = logging.getLogger(__name__ + '.DeleteClassifier')


class UpdateClassifier(neutronV20.UpdateCommand):
    """Update classifier's information."""

    resource = 'classifier'
    log = logging.getLogger(__name__ + '.UpdateClassifier')


class ListAction(neutronV20.ListCommand):
    """List actions that belong to a given tenant."""

    resource = 'action'
    log = logging.getLogger(__name__ + '.ListAction')
    _formatters = {}
    list_columns = ['id', 'name', 'description', 'action_type', 'action_value']
    pagination_support = True
    sorting_support = True


class ShowAction(neutronV20.ShowCommand):
    """Show information of a given action."""

    resource = 'action'
    log = logging.getLogger(__name__ + '.ShowAction')


class CreateAction(neutronV20.CreateCommand):
    """Create a action for a given tenant."""

    resource = 'action'
    log = logging.getLogger(__name__ + '.CreateAction')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the action'))
        parser.add_argument(
            '--action-type',
            #default='allow',
            choices=['allow', 'redirect'],
            help=_('Type of action'))
        parser.add_argument(
            '--action-value',
            #default='',
            help=_('uuid of service for redirect action'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of action to create'))

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description',
                                'action_type', 'action_value'])

        return body


class DeleteAction(neutronV20.DeleteCommand):
    """Delete a given action."""

    resource = 'action'
    log = logging.getLogger(__name__ + '.DeleteAction')


class UpdateAction(neutronV20.UpdateCommand):
    """Update action's information."""

    resource = 'action'
    log = logging.getLogger(__name__ + '.UpdateAction')


class ListBridgeDomain(neutronV20.ListCommand):
    """List bridge_domains that belong to a given tenant."""

    resource = 'bridge_domain'
    log = logging.getLogger(__name__ + '.ListBridgeDomain')
    _formatters = {}
    list_columns = ['id', 'name', 'description', 'routing_domain_id']
    pagination_support = True
    sorting_support = True


class ShowBridgeDomain(neutronV20.ShowCommand):
    """Show information of a given bridge_domain."""

    resource = 'bridge_domain'
    log = logging.getLogger(__name__ + '.ShowBridgeDomain')


class CreateBridgeDomain(neutronV20.CreateCommand):
    """Create a bridge_domain for a given tenant."""

    resource = 'bridge_domain'
    log = logging.getLogger(__name__ + '.CreateBridgeDomain')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the bridge_domain'))
        parser.add_argument(
            '--routing-domain',
            default='',
            help=_('routing_domain uuid'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of bridge_domain to create'))

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description'])
        if parsed_args.routing_domain:
            body[self.resource]['routing_domain_id'] = \
                neutronV20_find_resourceid_by_name_or_id(
                    self.get_client(), 'routing_domain',
                    parsed_args.routing_domain)

        return body


class DeleteBridgeDomain(neutronV20.DeleteCommand):
    """Delete a given bridge_domain."""

    resource = 'bridge_domain'
    log = logging.getLogger(__name__ + '.DeleteBridgeDomain')


class UpdateBridgeDomain(neutronV20.UpdateCommand):
    """Update bridge_domain's information."""

    resource = 'bridge_domain'
    log = logging.getLogger(__name__ + '.UpdateBridgeDomain')


class ListRoutingDomain(neutronV20.ListCommand):
    """List routing_domains that belong to a given tenant."""

    resource = 'routing_domain'
    log = logging.getLogger(__name__ + '.ListRoutingDomain')
    _formatters = {}
    list_columns = ['id', 'name', 'description', 'ip_supernet']
    pagination_support = True
    sorting_support = True


class ShowRoutingDomain(neutronV20.ShowCommand):
    """Show information of a given routing_domain."""

    resource = 'routing_domain'
    log = logging.getLogger(__name__ + '.ShowRoutingDomain')


class CreateRoutingDomain(neutronV20.CreateCommand):
    """Create a routing_domain for a given tenant."""

    resource = 'routing_domain'
    log = logging.getLogger(__name__ + '.CreateRoutingDomain')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of the routing_domain'))
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4, choices=[4, 6],
            help=_('IP version with default 4'))
        parser.add_argument(
            '--ip-supernet',
            help=_('CIDR of supernet to create'))
        parser.add_argument(
            '--subnet-prefix-length',
            type=int,
            default=24,
            help=_('Subnet prefix length [24]'))
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of routing_domain to create'))

    def args2body(self, parsed_args):
        body = {self.resource: {}, }

        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['name', 'tenant_id', 'description',
                                'ip_version', 'ip_supernet',
                                'subnet_prefix_length'])

        return body


class DeleteRoutingDomain(neutronV20.DeleteCommand):
    """Delete a given routing_domain."""

    resource = 'routing_domain'
    log = logging.getLogger(__name__ + '.DeleteRoutingDomain')


class UpdateRoutingDomain(neutronV20.UpdateCommand):
    """Update routing_domain's information."""

    resource = 'routing_domain'
    log = logging.getLogger(__name__ + '.UpdateRoutingDomain')
