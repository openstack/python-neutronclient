# Copyright 2016-2017 FUJITSU LIMITED
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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.fwaas import constants as const


LOG = logging.getLogger(__name__)

_formatters = {}


_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'description': 'Description',
    'firewall_rules': 'Firewall Rules',
    'audited': 'Audited',
    'shared': 'Shared',
    'tenant_id': 'Project',
    'project_id': 'Project',
}

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('firewall_rules', 'Firewall Rules', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('audited', 'Audited', column_util.LIST_LONG_ONLY),
    ('shared', 'Shared', column_util.LIST_LONG_ONLY),
    ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
)


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    client = client_manager.network

    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['tenant_id'] = osc_utils.find_project(
                client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
    if parsed_args.firewall_rule and parsed_args.no_firewall_rule:
        _firewall_rules = []
        for f in parsed_args.firewall_rule:
            _firewall_rules.append(client.find_firewall_rule(f)['id'])
        attrs[const.FWRS] = _firewall_rules
    elif parsed_args.firewall_rule:
        rules = []
        if not is_create:
            foobar = client.find_firewall_policy(
                parsed_args.firewall_policy)
            rules += foobar[const.FWRS]
        for f in parsed_args.firewall_rule:
            rules.append(client.find_firewall_rule(f)['id'])
        attrs[const.FWRS] = rules
    elif parsed_args.no_firewall_rule:
        attrs[const.FWRS] = []
    if parsed_args.audited:
        attrs['audited'] = True
    if parsed_args.no_audited:
        attrs['audited'] = False
    if parsed_args.name:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.description:
        attrs['description'] = str(parsed_args.description)
    if parsed_args.share:
        attrs['shared'] = True
    if parsed_args.no_share:
        attrs['shared'] = False
    return attrs


def _get_common_parser(parser):
    parser.add_argument(
        '--description',
        help=_('Description of the firewall policy'))
    audited_group = parser.add_mutually_exclusive_group()
    audited_group.add_argument(
        '--audited',
        action='store_true',
        help=_('Enable auditing for the policy'))
    audited_group.add_argument(
        '--no-audited',
        action='store_true',
        help=_('Disable auditing for the policy'))
    shared_group = parser.add_mutually_exclusive_group()
    shared_group.add_argument(
        '--share',
        action='store_true',
        help=_('Share the firewall policy to be used in all projects '
               '(by default, it is restricted to be used by the '
               'current project).'))
    shared_group.add_argument(
        '--no-share',
        action='store_true',
        help=_('Restrict use of the firewall policy to the '
               'current project'))
    return parser


class CreateFirewallPolicy(command.ShowOne):
    _description = _("Create a new firewall policy")

    def get_parser(self, prog_name):
        parser = super(CreateFirewallPolicy, self).get_parser(prog_name)
        _get_common_parser(parser)
        osc_utils.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name for the firewall policy'))
        fwr_group = parser.add_mutually_exclusive_group()
        fwr_group.add_argument(
            '--firewall-rule',
            action='append',
            metavar='<firewall-rule>',
            help=_('Firewall rule(s) to apply (name or ID)'))
        fwr_group.add_argument(
            '--no-firewall-rule',
            action='store_true',
            help=_('Unset all firewall rules from firewall policy'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        obj = client.create_firewall_policy(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


class DeleteFirewallPolicy(command.Command):
    _description = _("Delete firewall policy(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteFirewallPolicy, self).get_parser(prog_name)
        parser.add_argument(
            const.FWP,
            metavar='<firewall-policy>',
            nargs='+',
            help=_('Firewall policy(s) to delete (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for fwp in parsed_args.firewall_policy:
            try:
                fwp_id = client.find_firewall_policy(fwp)['id']
                client.delete_firewall_policy(fwp_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete Firewall policy with "
                            "name or ID '%(firewall_policy)s': %(e)s"),
                          {const.FWP: fwp, 'e': e})

        if result > 0:
            total = len(parsed_args.firewall_policy)
            msg = (_("%(result)s of %(total)s firewall policy(s) "
                     "failed to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class FirewallPolicyInsertRule(command.Command):
    _description = _("Insert a rule into a given firewall policy")

    def get_parser(self, prog_name):
        parser = super(FirewallPolicyInsertRule, self).get_parser(prog_name)
        parser.add_argument(
            const.FWP,
            metavar='<firewall-policy>',
            help=_('Firewall policy to insert rule (name or ID)'))
        parser.add_argument(
            '--insert-before',
            metavar='<firewall-rule>',
            help=_('Insert the new rule before this existing rule  '
                   '(name or ID)'))
        parser.add_argument(
            '--insert-after',
            metavar='<firewall-rule>',
            help=_('Insert the new rule after this existing rule  '
                   '(name or ID)'))
        parser.add_argument(
            const.FWR,
            metavar='<firewall-rule>',
            help=_('Firewall rule to be inserted (name or ID)'))
        return parser

    def args2body(self, parsed_args):
        client = self.app.client_manager.network
        _rule_id = _get_required_firewall_rule(client, parsed_args)
        _insert_before = ''
        if 'insert_before' in parsed_args:
            if parsed_args.insert_before:
                _insert_before = client.find_firewall_rule(
                    parsed_args.insert_before)['id']
        _insert_after = ''
        if 'insert_after' in parsed_args:
            if parsed_args.insert_after:
                _insert_after = client.find_firewall_rule(
                    parsed_args.insert_after)['id']
        return {'firewall_rule_id': _rule_id,
                'insert_before': _insert_before,
                'insert_after': _insert_after}

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        policy_id = client.find_firewall_policy(
            parsed_args.firewall_policy)['id']
        body = self.args2body(parsed_args)
        client.insert_rule_into_policy(policy_id, **body)
        rule_id = body['firewall_rule_id']
        policy = parsed_args.firewall_policy
        print((_('Inserted firewall rule %(rule)s in firewall policy '
                 '%(policy)s') % {'rule': rule_id, 'policy': policy}),
              file=self.app.stdout)


class FirewallPolicyRemoveRule(command.Command):
    _description = _("Remove a rule from a given firewall policy")

    def get_parser(self, prog_name):
        parser = super(FirewallPolicyRemoveRule, self).get_parser(prog_name)
        parser.add_argument(
            const.FWP,
            metavar='<firewall-policy>',
            help=_('Firewall policy to remove rule (name or ID)'))
        parser.add_argument(
            const.FWR,
            metavar='<firewall-rule>',
            help=_('Firewall rule to remove from policy (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        policy_id = client.find_firewall_policy(
            parsed_args.firewall_policy)['id']
        fwr_id = _get_required_firewall_rule(client, parsed_args)
        body = {'firewall_rule_id': fwr_id}
        client.remove_rule_from_policy(policy_id, **body)
        rule_id = body['firewall_rule_id']
        policy = parsed_args.firewall_policy
        print((_('Removed firewall rule %(rule)s from firewall policy '
                 '%(policy)s') % {'rule': rule_id, 'policy': policy}),
              file=self.app.stdout)


class ListFirewallPolicy(command.Lister):
    _description = _("List firewall policies")

    def get_parser(self, prog_name):
        parser = super(ListFirewallPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.firewall_policies()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(
            s, columns, formatters=_formatters) for s in obj))


class SetFirewallPolicy(command.Command):
    _description = _("Set firewall policy properties")

    def get_parser(self, prog_name):
        parser = super(SetFirewallPolicy, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            const.FWP,
            metavar='<firewall-policy>',
            help=_('Firewall policy to update (name or ID)'))
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name for the firewall policy'))
        parser.add_argument(
            '--firewall-rule',
            action='append',
            metavar='<firewall-rule>',
            help=_('Firewall rule(s) to apply (name or ID)'))
        parser.add_argument(
            '--no-firewall-rule',
            action='store_true',
            help=_('Remove all firewall rules from firewall policy'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fwp_id = client.find_firewall_policy(
            parsed_args.firewall_policy)['id']
        attrs = _get_common_attrs(self.app.client_manager,
                                  parsed_args, is_create=False)
        try:
            client.update_firewall_policy(fwp_id, **attrs)
        except Exception as e:
            msg = (_("Failed to set firewall policy '%(policy)s': %(e)s")
                   % {'policy': parsed_args.firewall_policy, 'e': e})
            raise exceptions.CommandError(msg)


class ShowFirewallPolicy(command.ShowOne):
    _description = _("Display firewall policy details")

    def get_parser(self, prog_name):
        parser = super(ShowFirewallPolicy, self).get_parser(prog_name)
        parser.add_argument(
            const.FWP,
            metavar='<firewall-policy>',
            help=_('Firewall policy to show (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fwp_id = client.find_firewall_policy(
            parsed_args.firewall_policy)['id']
        obj = client.get_firewall_policy(fwp_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)


def _get_required_firewall_rule(client, parsed_args):
    if not parsed_args.firewall_rule:
        msg = (_("Firewall rule (name or ID) is required."))
        raise exceptions.CommandError(msg)
    return client.find_firewall_rule(parsed_args.firewall_rule)['id']


class UnsetFirewallPolicy(command.Command):
    _description = _("Unset firewall policy properties")

    def get_parser(self, prog_name):
        parser = super(UnsetFirewallPolicy, self).get_parser(prog_name)
        parser.add_argument(
            const.FWP,
            metavar='<firewall-policy>',
            help=_('Firewall policy to unset (name or ID)'))
        firewall_rule_group = parser.add_mutually_exclusive_group()
        firewall_rule_group.add_argument(
            '--firewall-rule',
            action='append',
            metavar='<firewall-rule>',
            help=_('Remove firewall rule(s) from the firewall policy '
                   '(name or ID)'))
        firewall_rule_group.add_argument(
            '--all-firewall-rule',
            action='store_true',
            help=_('Remove all firewall rules from the firewall policy'))
        parser.add_argument(
            '--audited',
            action='store_true',
            help=_('Disable auditing for the policy'))
        parser.add_argument(
            '--share',
            action='store_true',
            help=_('Restrict use of the firewall policy to the '
                   'current project'))
        return parser

    def _get_attrs(self, client_manager, parsed_args):
        attrs = {}
        client = client_manager.network

        if parsed_args.firewall_rule:
            current = client.find_firewall_policy(
                parsed_args.firewall_policy)[const.FWRS]
            removed = []
            for f in set(parsed_args.firewall_rule):
                removed.append(client.find_firewall_rule(f)['id'])
            attrs[const.FWRS] = [r for r in current if r not in removed]
        if parsed_args.all_firewall_rule:
            attrs[const.FWRS] = []
        if parsed_args.audited:
            attrs['audited'] = False
        if parsed_args.share:
            attrs['shared'] = False
        return attrs

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fwp_id = client.find_firewall_policy(
            parsed_args.firewall_policy)['id']
        attrs = self._get_attrs(self.app.client_manager, parsed_args)
        try:
            client.update_firewall_policy(fwp_id, **attrs)
        except Exception as e:
            msg = (_("Failed to unset firewall policy '%(policy)s': %(e)s")
                   % {'policy': parsed_args.firewall_policy, 'e': e})
            raise exceptions.CommandError(msg)
