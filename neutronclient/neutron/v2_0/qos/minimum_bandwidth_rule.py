# Copyright (c) 2016 Intel Corporation.
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
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.qos import rule as qos_rule


MINIMUM_BANDWIDTH_RULE_RESOURCE = 'minimum_bandwidth_rule'


def add_minimum_bandwidth_arguments(parser):
    parser.add_argument(
        '--min-kbps',
        required=True,
        type=str,
        help=_('QoS minimum bandwidth assurance, expressed in kilobits '
               'per second.'))
    # NOTE(ralonsoh): the only direction implemented is "egress". Please,
    # refer to the spec (https://review.openstack.org/#/c/316082/).
    parser.add_argument(
        '--direction',
        # NOTE(ihrachys): though server picks the default for us (egress), it's
        # better to require the argument to make the UI more explicit and the
        # intentions more clear in the future when we add other values for the
        # attribute on server side.
        required=True,
        type=utils.convert_to_lowercase,
        choices=['egress'],
        help=_('Traffic direction.'))


def update_minimum_bandwidth_args2body(parsed_args, body):
    neutronv20.update_dict(parsed_args, body, ['min_kbps', 'direction'])


class CreateQoSMinimumBandwidthRule(qos_rule.QosRuleMixin,
                                    neutronv20.CreateCommand):
    """Create a qos minimum bandwidth rule."""

    resource = MINIMUM_BANDWIDTH_RULE_RESOURCE

    def add_known_arguments(self, parser):
        super(CreateQoSMinimumBandwidthRule, self).add_known_arguments(
            parser)
        add_minimum_bandwidth_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        update_minimum_bandwidth_args2body(parsed_args, body)
        return {self.resource: body}


class ListQoSMinimumBandwidthRules(qos_rule.QosRuleMixin,
                                   neutronv20.ListCommand):
    """List all qos minimum bandwidth rules belonging to the specified policy.

    """

    resource = MINIMUM_BANDWIDTH_RULE_RESOURCE
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowQoSMinimumBandwidthRule(qos_rule.QosRuleMixin,
                                  neutronv20.ShowCommand):
    """Show information about the given qos minimum bandwidth rule."""

    resource = MINIMUM_BANDWIDTH_RULE_RESOURCE
    allow_names = False


class UpdateQoSMinimumBandwidthRule(qos_rule.QosRuleMixin,
                                    neutronv20.UpdateCommand):
    """Update the given qos minimum bandwidth rule."""

    resource = MINIMUM_BANDWIDTH_RULE_RESOURCE
    allow_names = False

    def add_known_arguments(self, parser):
        super(UpdateQoSMinimumBandwidthRule, self).add_known_arguments(
            parser)
        add_minimum_bandwidth_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        update_minimum_bandwidth_args2body(parsed_args, body)
        return {self.resource: body}


class DeleteQoSMinimumBandwidthRule(qos_rule.QosRuleMixin,
                                    neutronv20.DeleteCommand):
    """Delete a given qos minimum bandwidth rule."""

    resource = MINIMUM_BANDWIDTH_RULE_RESOURCE
    allow_names = False
