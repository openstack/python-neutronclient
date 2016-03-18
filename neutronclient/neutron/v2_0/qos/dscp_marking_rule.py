# Copyright 2016 Comcast, Inc.
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


DSCP_MARKING_RESOURCE = 'dscp_marking_rule'
# DSCP DETAILS
# 0 - none  | 8 - cs1   | 10 - af11 | 12 - af12 | 14 - af13 |
# 16 - cs2  | 18 - af21 | 20 - af22 | 22 - af23 | 24 - cs3  |
# 26 - af31 | 28 - af32 | 30 - af33 | 32 - cs4  | 34 - af41 |
# 36 - af42 | 38 - af43 | 40 - cs5  | 46 - ef   | 48 - cs6  |
# 56 - cs7

DSCP_VALID_MARKS = [0, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32,
                    34, 36, 38, 40, 46, 48, 56]


def add_dscp_marking_arguments(parser):
    parser.add_argument(
        '--dscp-mark',
        required=True,
        type=str,
        help=_('DSCP mark: value can be 0, even numbers from 8-56, \
                excluding 42, 44, 50, 52, and 54.'))


def update_dscp_args2body(parsed_args, body):
    dscp_mark = parsed_args.dscp_mark
    if int(dscp_mark) not in DSCP_VALID_MARKS:
        raise exceptions.CommandError(_("DSCP mark: %s not supported. "
                                        "Please note value can either be 0 "
                                        "or any even number from 8-56 "
                                        "excluding 42, 44, 50, 52 and "
                                        "54.") % dscp_mark)
    neutronv20.update_dict(parsed_args, body,
                           ['dscp_mark'])


class CreateQoSDscpMarkingRule(qos_rule.QosRuleMixin,
                               neutronv20.CreateCommand):
    """Create a QoS DSCP marking rule."""

    resource = DSCP_MARKING_RESOURCE

    def add_known_arguments(self, parser):
        super(CreateQoSDscpMarkingRule, self).add_known_arguments(parser)
        add_dscp_marking_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        update_dscp_args2body(parsed_args, body)
        return {self.resource: body}


class ListQoSDscpMarkingRules(qos_rule.QosRuleMixin,
                              neutronv20.ListCommand):
    """List all QoS DSCP marking rules belonging to the specified policy."""

    _formatters = {}
    pagination_support = True
    sorting_support = True
    resource = DSCP_MARKING_RESOURCE


class ShowQoSDscpMarkingRule(qos_rule.QosRuleMixin,
                             neutronv20.ShowCommand):
    """Show information about the given qos dscp marking rule."""

    resource = DSCP_MARKING_RESOURCE
    allow_names = False


class UpdateQoSDscpMarkingRule(qos_rule.QosRuleMixin,
                               neutronv20.UpdateCommand):
    """Update the given QoS DSCP marking rule."""

    allow_names = False
    resource = DSCP_MARKING_RESOURCE

    def add_known_arguments(self, parser):
        super(UpdateQoSDscpMarkingRule, self).add_known_arguments(parser)
        add_dscp_marking_arguments(parser)

    def args2body(self, parsed_args):
        body = {}
        update_dscp_args2body(parsed_args, body)
        return {self.resource: body}


class DeleteQoSDscpMarkingRule(qos_rule.QosRuleMixin,
                               neutronv20.DeleteCommand):
    """Delete a given qos dscp marking rule."""

    allow_names = False
    resource = DSCP_MARKING_RESOURCE
