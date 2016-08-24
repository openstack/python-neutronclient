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
from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronv20
from neutronclient.neutron.v2_0.qos import rule as qos_rule


BANDWIDTH_LIMIT_RULE_RESOURCE = 'bandwidth_limit_rule'


def add_bandwidth_limit_arguments(parser):
    parser.add_argument(
        '--max-kbps',
        help=_('Maximum bandwidth in kbps.'))
    parser.add_argument(
        '--max-burst-kbps',
        help=_('Maximum burst bandwidth in kbps.'))


def update_bandwidth_limit_args2body(parsed_args, body):
    max_kbps = parsed_args.max_kbps
    max_burst_kbps = parsed_args.max_burst_kbps
    if not (max_kbps or max_burst_kbps):
        raise exceptions.CommandError(_("Must provide max-kbps"
                                        " or max-burst-kbps option."))
    neutronv20.update_dict(parsed_args, body,
                           ['max_kbps', 'max_burst_kbps', 'tenant_id'])


class CreateQoSBandwidthLimitRule(qos_rule.QosRuleMixin,
                                  neutronv20.CreateCommand):
    """Create a qos bandwidth limit rule."""

    resource = BANDWIDTH_LIMIT_RULE_RESOURCE

    def add_known_arguments(self, parser):
        super(CreateQoSBandwidthLimitRule, self).add_known_arguments(parser)
        add_bandwidth_limit_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        update_bandwidth_limit_args2body(parsed_args, body)
        return {self.resource: body}


class ListQoSBandwidthLimitRules(qos_rule.QosRuleMixin,
                                 neutronv20.ListCommand):
    """List all qos bandwidth limit rules belonging to the specified policy."""

    resource = BANDWIDTH_LIMIT_RULE_RESOURCE
    _formatters = {}
    pagination_support = True
    sorting_support = True


class ShowQoSBandwidthLimitRule(qos_rule.QosRuleMixin, neutronv20.ShowCommand):
    """Show information about the given qos bandwidth limit rule."""

    resource = BANDWIDTH_LIMIT_RULE_RESOURCE
    allow_names = False


class UpdateQoSBandwidthLimitRule(qos_rule.QosRuleMixin,
                                  neutronv20.UpdateCommand):
    """Update the given qos bandwidth limit rule."""

    resource = BANDWIDTH_LIMIT_RULE_RESOURCE
    allow_names = False

    def add_known_arguments(self, parser):
        super(UpdateQoSBandwidthLimitRule, self).add_known_arguments(parser)
        add_bandwidth_limit_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        update_bandwidth_limit_args2body(parsed_args, body)
        return {self.resource: body}


class DeleteQoSBandwidthLimitRule(qos_rule.QosRuleMixin,
                                  neutronv20.DeleteCommand):
    """Delete a given qos bandwidth limit rule."""

    resource = BANDWIDTH_LIMIT_RULE_RESOURCE
    allow_names = False
