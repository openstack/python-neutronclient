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


from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.qos import policy as qos_policy


def add_policy_argument(parser):
    parser.add_argument(
        'policy', metavar='QOS_POLICY',
        help=_('ID or name of the QoS policy.'))


def add_rule_argument(parser):
    parser.add_argument(
        'rule', metavar='QOS_RULE',
        help=_('ID of the QoS rule.'))


def update_policy_args2body(parsed_args, body):
    neutronv20.update_dict(parsed_args, body, ['policy'])


def update_rule_args2body(parsed_args, body):
    neutronv20.update_dict(parsed_args, body, ['rule'])


class QosRuleMixin(object):
    def add_known_arguments(self, parser):
        add_policy_argument(parser)

    def set_extra_attrs(self, parsed_args):
        self.parent_id = qos_policy.get_qos_policy_id(self.get_client(),
                                                      parsed_args.policy)

    def args2body(self, parsed_args):
        body = {}
        update_policy_args2body(parsed_args, body)
        return {'qos_rule': body}


class ListQoSRuleTypes(neutronv20.ListCommand):
    """List available qos rule types."""

    resource = 'rule_type'
    shadow_resource = 'qos_rule_type'
    pagination_support = True
    sorting_support = True
