# Copyright 2016 Radware LTD.
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


from neutronclient._i18n import _
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


def _get_policy_id(client, policy_id_or_name):
    return neutronV20.find_resourceid_by_name_or_id(
        client, 'l7policy', policy_id_or_name,
        cmd_resource='lbaas_l7policy')


class LbaasL7RuleMixin(object):

    def set_extra_attrs(self, parsed_args):
        self.parent_id = _get_policy_id(self.get_client(),
                                        parsed_args.l7policy)

    def add_known_arguments(self, parser):
        parser.add_argument(
            'l7policy', metavar='L7POLICY',
            help=_('ID or name of L7 policy this rule belongs to.'))


def _add_common_args(parser, is_create=True):
        parser.add_argument(
            '--type',
            required=is_create,
            type=utils.convert_to_uppercase,
            choices=['HOST_NAME', 'PATH', 'FILE_TYPE', 'HEADER', 'COOKIE'],
            help=_('Rule type.'))
        parser.add_argument(
            '--compare-type',
            required=is_create,
            type=utils.convert_to_uppercase,
            choices=['REGEX', 'STARTS_WITH', 'ENDS_WITH',
                     'CONTAINS', 'EQUAL_TO'],
            help=_('Rule compare type.'))
        parser.add_argument(
            '--invert-compare',
            dest='invert',
            action='store_true',
            help=_('Invert the compare type.'))
        parser.add_argument(
            '--key',
            help=_('Key to compare.'
                   ' Relevant for HEADER and COOKIE types only.'))
        parser.add_argument(
            '--value',
            required=is_create,
            help=_('Value to compare.'))


def _common_args2body(client, parsed_args, is_create=True):
    attributes = ['type', 'compare_type',
                  'invert', 'key', 'value', 'admin_state_up']
    if is_create:
        attributes.append('tenant_id')
    body = {}
    neutronV20.update_dict(parsed_args, body, attributes)
    return {'rule': body}


class ListL7Rule(LbaasL7RuleMixin, neutronV20.ListCommand):
    """LBaaS v2 List L7 rules that belong to a given L7 policy."""

    resource = 'rule'
    shadow_resource = 'lbaas_l7rule'
    pagination_support = True
    sorting_support = True

    list_columns = [
        'id', 'type', 'compare_type', 'invert', 'key', 'value',
        'admin_state_up', 'status'
    ]

    def take_action(self, parsed_args):
        self.parent_id = _get_policy_id(self.get_client(),
                                        parsed_args.l7policy)
        self.values_specs.append('--l7policy_id=%s' % self.parent_id)
        return super(ListL7Rule, self).take_action(parsed_args)


class ShowL7Rule(LbaasL7RuleMixin, neutronV20.ShowCommand):
    """LBaaS v2 Show information of a given rule."""

    resource = 'rule'
    shadow_resource = 'lbaas_l7rule'


class CreateL7Rule(LbaasL7RuleMixin, neutronV20.CreateCommand):
    """LBaaS v2 Create L7 rule."""

    resource = 'rule'
    shadow_resource = 'lbaas_l7rule'

    def add_known_arguments(self, parser):
        super(CreateL7Rule, self).add_known_arguments(parser)
        _add_common_args(parser)
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state_up',
            action='store_false',
            help=_('Set admin state up to false'))

    def args2body(self, parsed_args):
        return _common_args2body(self.get_client(), parsed_args)


class UpdateL7Rule(LbaasL7RuleMixin, neutronV20.UpdateCommand):
    """LBaaS v2 Update a given L7 rule."""

    resource = 'rule'
    shadow_resource = 'lbaas_l7rule'

    def add_known_arguments(self, parser):
        super(UpdateL7Rule, self).add_known_arguments(parser)
        _add_common_args(parser, False)
        utils.add_boolean_argument(
            parser, '--admin-state-up',
            help=_('Specify the administrative state of the rule'
                   ' (True meaning "Up").'))

    def args2body(self, parsed_args):
        return _common_args2body(self.get_client(), parsed_args, False)


class DeleteL7Rule(LbaasL7RuleMixin, neutronV20.DeleteCommand):
    """LBaaS v2 Delete a given L7 rule."""

    resource = 'rule'
    shadow_resource = 'lbaas_l7rule'
