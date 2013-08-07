# Copyright 2013 Big Switch Networks
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
# @author: KC Wang, Big Switch Networks
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import json
import logging
import string

from neutronclient.neutron import v2_0 as neutronv20


def _format_firewall_rules(firewall_policy):
    try:
        output = '[' + ',\n '.join([rule for rule in
                                    firewall_policy['firewall_rules']]) + ']'
        return output
    except Exception:
        return ''


class ListFirewallPolicy(neutronv20.ListCommand):
    """List firewall policies that belong to a given tenant."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.ListFirewallPolicy')
    list_columns = ['id', 'name', 'firewall_rules']
    _formatters = {'firewall_rules': _format_firewall_rules,
                   }
    pagination_support = True
    sorting_support = True


class ShowFirewallPolicy(neutronv20.ShowCommand):
    """Show information of a given firewall policy."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.ShowFirewallPolicy')


class CreateFirewallPolicy(neutronv20.CreateCommand):
    """Create a firewall policy."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.CreateFirewallPolicy')

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='NAME',
            help='name for the firewall policy')
        parser.add_argument(
            '--description',
            help='description for the firewall policy')
        parser.add_argument(
            '--shared',
            dest='shared',
            action='store_true',
            help='to create a shared policy')
        parser.add_argument(
            '--firewall-rules', type=string.split,
            help='ordered list of whitespace-delimited firewall rule '
            'names or IDs; e.g., --firewall-rules \"rule1 rule2\"')
        parser.add_argument(
            '--audited',
            action='store_true',
            help='to set audited to True')

    def args2body(self, parsed_args):
        if parsed_args.firewall_rules:
            _firewall_rules = []
            for f in parsed_args.firewall_rules:
                _firewall_rules.append(
                    neutronv20.find_resourceid_by_name_or_id(
                        self.get_client(), 'firewall_rule', f))
                body = {self.resource: {
                        'firewall_rules': _firewall_rules,
                        },
                        }
        else:
            body = {self.resource: {}}
        neutronv20.update_dict(parsed_args, body[self.resource],
                               ['name', 'description', 'shared',
                                'audited', 'tenant_id'])
        return body


class UpdateFirewallPolicy(neutronv20.UpdateCommand):
    """Update a given firewall policy."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.UpdateFirewallPolicy')


class DeleteFirewallPolicy(neutronv20.DeleteCommand):
    """Delete a given firewall policy."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.DeleteFirewallPolicy')


class FirewallPolicyInsertRule(neutronv20.UpdateCommand):
    """Insert a rule into a given firewall policy."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.FirewallPolicyInsertRule')

    def call_api(self, neutron_client, firewall_policy_id, body):
        return neutron_client.firewall_policy_insert_rule(firewall_policy_id,
                                                          body)

    def args2body(self, parsed_args):
        _rule = ''
        if parsed_args.firewall_rule_id:
            _rule = neutronv20.find_resourceid_by_name_or_id(
                self.get_client(), 'firewall_rule',
                parsed_args.firewall_rule_id)
        _insert_before = ''
        if 'insert_before' in parsed_args:
            if parsed_args.insert_before:
                _insert_before = neutronv20.find_resourceid_by_name_or_id(
                    self.get_client(), 'firewall_rule',
                    parsed_args.insert_before)
        _insert_after = ''
        if 'insert_after' in parsed_args:
            if parsed_args.insert_after:
                _insert_after = neutronv20.find_resourceid_by_name_or_id(
                    self.get_client(), 'firewall_rule',
                    parsed_args.insert_after)
        body = {'firewall_rule_id': _rule,
                'insert_before': _insert_before,
                'insert_after': _insert_after}
        neutronv20.update_dict(parsed_args, body, [])
        return body

    def get_parser(self, prog_name):
        parser = super(FirewallPolicyInsertRule, self).get_parser(prog_name)
        parser.add_argument(
            '--insert-before',
            metavar='FIREWALL_RULE',
            help='insert before this rule')
        parser.add_argument(
            '--insert-after',
            metavar='FIREWALL_RULE',
            help='insert after this rule')
        parser.add_argument(
            'firewall_rule_id',
            metavar='FIREWALL_RULE',
            help='new rule to insert')
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _id = neutronv20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        policy_data = self.call_api(neutron_client, _id, body)
        print json.dumps(policy_data)
        return


class FirewallPolicyRemoveRule(neutronv20.UpdateCommand):
    """Remove a rule from a given firewall policy."""

    resource = 'firewall_policy'
    log = logging.getLogger(__name__ + '.FirewallPolicyRemoveRule')

    def call_api(self, neutron_client, firewall_policy_id, body):
        return neutron_client.firewall_policy_remove_rule(firewall_policy_id,
                                                          body)

    def args2body(self, parsed_args):
        _rule = ''
        if parsed_args.firewall_rule_id:
            _rule = neutronv20.find_resourceid_by_name_or_id(
                self.get_client(), 'firewall_rule',
                parsed_args.firewall_rule_id)
        body = {'firewall_rule_id': _rule}
        neutronv20.update_dict(parsed_args, body, [])
        return body

    def get_parser(self, prog_name):
        parser = super(FirewallPolicyRemoveRule, self).get_parser(prog_name)
        parser.add_argument(
            'firewall_rule_id',
            metavar='FIREWALL_RULE',
            help='firewall rule to remove from policy')
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _id = neutronv20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        policy_data = self.call_api(neutron_client, _id, body)
        print json.dumps(policy_data)
        return
