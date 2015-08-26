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

import sys

from neutronclient.neutron.v2_0.lb.v2 import l7rule
from neutronclient.tests.unit import test_cli20


"""Structure for mapping cli and api arguments

The structure maps cli arguments and a list of its
api argument name, default cli value and default api value.
It helps to make tests more general for different argument types.
"""
args_conf = {
    'admin-state-up': ['admin_state_up', True, True],
    'admin-state-down': ['admin_state_up', None, False],
    'type': ['type', 'HOST_NAME', 'HOST_NAME'],
    'compare-type': ['compare_type', 'EQUAL_TO', 'EQUAL_TO'],
    'invert-compare': ['invert', None, True],
    'key': ['key', 'key', 'key'],
    'value': ['value', 'value', 'value']}


class CLITestV20LbL7RuleJSON(test_cli20.CLITestV20Base):

    def _get_test_args(self, *args, **kwargs):
        """Function for generically building testing arguments"""
        cli_args = []
        api_args = {}
        for arg in args:
            cli_args.append('--' + arg)
            if not args_conf[arg][1]:
                pass
            elif arg in kwargs:
                cli_args.append(str(kwargs[arg]))
            else:
                cli_args.append(args_conf[arg][1])

            if arg in kwargs:
                api_args[args_conf[arg][0]] = kwargs[arg]
            else:
                api_args[args_conf[arg][0]] = args_conf[arg][2]

        if 'invert' not in api_args:
            api_args['invert'] = False
        return cli_args, api_args

    def _test_create_rule(self, *args, **kwargs):
        resource = 'rule'
        cmd_resource = 'lbaas_l7rule'
        cmd = l7rule.CreateL7Rule(test_cli20.MyApp(sys.stdout), None)
        cli_args, api_args = self._get_test_args(*args, **kwargs)
        position_names = list(api_args.keys())
        position_values = list(api_args.values())
        cli_args.append('test_policy')
        self._test_create_resource(resource, cmd, None, 'test_id',
                                   cli_args, position_names, position_values,
                                   cmd_resource=cmd_resource,
                                   parent_id='test_policy')

    def _test_update_rule(self, *args, **kwargs):
        resource = 'rule'
        cmd_resource = 'lbaas_l7rule'
        cmd = l7rule.UpdateL7Rule(test_cli20.MyApp(sys.stdout), None)
        cli_args, api_args = self._get_test_args(*args, **kwargs)
        cli_args.append('test_id')
        cli_args.append('test_policy')
        self._test_update_resource(resource, cmd, 'test_id',
                                   cli_args, api_args,
                                   cmd_resource=cmd_resource,
                                   parent_id='test_policy')

    def test_create_rule_with_mandatory_params(self):
        # lbaas-l7rule-create with mandatory params only.

        self._test_create_rule('type', 'compare-type',
                               'value')

    def test_create_disabled_rule(self):
        # lbaas-l7rule-create disabled rule.

        self._test_create_rule('type', 'compare-type',
                               'value', 'admin-state-down')

    def test_create_rule_with_all_params(self):
        # lbaas-l7rule-create with all params set.

        self._test_create_rule('type', 'compare-type',
                               'invert-compare', 'key', 'value',
                               type='HEADER', compare_type='CONTAINS',
                               key='other_key', value='other_value')

    def test_create_rule_with_inverted_compare(self):
        # lbaas-l7rule-create with invertted compare type.

        self._test_create_rule('type', 'compare-type',
                               'invert-compare', 'value')

    def test_list_rules(self):
        # lbaas-l7rule-list.

        resources = 'rules'
        cmd_resources = 'lbaas_l7rules'
        cmd = l7rule.ListL7Rule(test_cli20.MyApp(sys.stdout), None)

        policy_id = 'policy_id'
        self._test_list_resources(resources, cmd, True,
                                  base_args=[policy_id],
                                  cmd_resources=cmd_resources,
                                  parent_id=policy_id,
                                  query="l7policy_id=%s" % policy_id)

    def test_list_rules_pagination(self):
        # lbaas-l7rule-list with pagination.

        resources = 'rules'
        cmd_resources = 'lbaas_l7rules'
        cmd = l7rule.ListL7Rule(test_cli20.MyApp(sys.stdout), None)
        policy_id = 'policy_id'
        self._test_list_resources_with_pagination(
            resources, cmd, base_args=[policy_id],
            cmd_resources=cmd_resources, parent_id=policy_id,
            query="l7policy_id=%s" % policy_id)

    def test_list_rules_sort(self):
        # lbaas-l7rule-list --sort-key id --sort-key asc.

        resources = 'rules'
        cmd_resources = 'lbaas_l7rules'
        cmd = l7rule.ListL7Rule(test_cli20.MyApp(sys.stdout), None)
        policy_id = 'policy_id'
        self._test_list_resources(
            resources, cmd, True, base_args=[policy_id],
            cmd_resources=cmd_resources, parent_id=policy_id,
            query="l7policy_id=%s" % policy_id)

    def test_list_rules_limit(self):
        # lbaas-l7rule-list -P.

        resources = 'rules'
        cmd_resources = 'lbaas_l7rules'
        cmd = l7rule.ListL7Rule(test_cli20.MyApp(sys.stdout), None)
        policy_id = 'policy_id'
        self._test_list_resources(resources, cmd, page_size=1000,
                                  base_args=[policy_id],
                                  cmd_resources=cmd_resources,
                                  parent_id=policy_id,
                                  query="l7policy_id=%s" % policy_id)

    def test_show_rule_id(self):
        # lbaas-l7rule-show test_id.

        resource = 'rule'
        cmd_resource = 'lbaas_l7rule'
        policy_id = 'policy_id'
        cmd = l7rule.ShowL7Rule(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id, policy_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'],
                                 cmd_resource=cmd_resource,
                                 parent_id=policy_id)

    def test_update_rule_type(self):
        # lbaas-l7rule-update test_id --type HEADER test_policy

        self._test_update_rule('type', type='HEADER')

    def test_update_rule_compare_type(self):
        # lbaas-l7rule-update test_id --compare-type CONTAINS test_policy.

        self._test_update_rule('compare-type',
                               **{'compare-type': 'CONTAINS'})

    def test_update_rule_inverted_compare_type(self):
        # lbaas-l7rule-update test_id --invert-compare test_policy.

        self._test_update_rule('invert-compare')

    def test_update_rule_key_value(self):
        # lbaas-l7rule-update test_id --key other --value other test_policy.

        self._test_update_rule('key', 'value',
                               key='other', value='other')

    def test_delete_rule(self):
        # lbaas-l7rule-delete test_id policy_id.

        resource = 'rule'
        cmd_resource = 'lbaas_l7rule'
        policy_id = 'policy_id'
        test_id = 'test_id'
        cmd = l7rule.DeleteL7Rule(test_cli20.MyApp(sys.stdout), None)
        args = [test_id, policy_id]
        self._test_delete_resource(resource, cmd, test_id, args,
                                   cmd_resource=cmd_resource,
                                   parent_id=policy_id)
