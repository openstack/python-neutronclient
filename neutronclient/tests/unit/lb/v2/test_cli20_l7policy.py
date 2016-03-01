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

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0.lb.v2 import l7policy
from neutronclient.tests.unit import test_cli20

"""Structure for mapping cli and api arguments

The structure maps cli arguments and a list of its
api argument name, default cli value and default api value.
It helps to make tests more general for different argument types.
"""
args_conf = {
    'name': ['name', 'test_policy', 'test_policy'],
    'description': ['description', 'test policy', 'test policy'],
    'listener': ['listener_id', 'test_listener', 'test_listener'],
    'admin-state-up': ['admin_state_up', True, True],
    'admin-state-down': ['admin_state_up', None, False],
    'action': ['action', 'REJECT', 'REJECT'],
    'redirect-url': ['redirect_url', 'http://url', 'http://url'],
    'redirect-pool': ['redirect_pool_id', 'test_pool', 'test_pool'],
    'position': ['position', '1', 1]}


class CLITestV20LbL7PolicyJSON(test_cli20.CLITestV20Base):

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

        return cli_args, api_args

    def _test_create_policy(self, *args, **kwargs):
        resource = 'l7policy'
        cmd_resource = 'lbaas_l7policy'
        cmd = l7policy.CreateL7Policy(test_cli20.MyApp(sys.stdout), None)
        cli_args, api_args = self._get_test_args(*args, **kwargs)
        position_names = list(api_args.keys())
        position_values = list(api_args.values())
        self._test_create_resource(resource, cmd, None, 'test_id',
                                   cli_args, position_names, position_values,
                                   cmd_resource=cmd_resource)

    def _test_update_policy(self, *args, **kwargs):
        resource = 'l7policy'
        cmd_resource = 'lbaas_l7policy'
        cmd = l7policy.UpdateL7Policy(test_cli20.MyApp(sys.stdout), None)
        cli_args, api_args = self._get_test_args(*args, **kwargs)
        cli_args.append('test_id')
        self._test_update_resource(resource, cmd, 'test_id',
                                   cli_args, api_args,
                                   cmd_resource=cmd_resource)

    def test_create_policy_with_mandatory_params(self):
        # lbaas-l7policy-create with mandatory params only.
        self._test_create_policy('action', 'listener')

    def test_create_policy_with_all_params(self):
        # lbaas-l7policy-create REJECT policy.
        self._test_create_policy('name', 'description',
                                 'action', 'listener',
                                 'position')

    def test_create_disabled_policy(self):
        # lbaas-l7policy-create disabled REJECT policy.
        self._test_create_policy('action', 'listener', 'admin-state-down')

    def test_create_url_redirect_policy(self):
        # lbaas-l7policy-create REDIRECT_TO_URL policy.
        self._test_create_policy('name', 'description',
                                 'action', 'listener',
                                 'redirect-url',
                                 action='REDIRECT_TO_URL')

    def test_create_url_redirect_policy_no_url(self):
        # lbaas-l7policy-create REDIRECT_TO_URL policy without url argument.
        self.assertRaises(exceptions.CommandError,
                          self._test_create_policy,
                          'name', 'description',
                          'action', 'listener',
                          action='REDIRECT_TO_URL')

    def test_create_pool_redirect_policy(self):
        # lbaas-l7policy-create REDIRECT_TO_POOL policy.
        self._test_create_policy('name', 'description',
                                 'action', 'listener',
                                 'redirect-pool',
                                 action='REDIRECT_TO_POOL')

    def test_create_pool_redirect_policy_no_pool(self):
        # lbaas-l7policy-create REDIRECT_TO_POOL policy without pool argument.
        self.assertRaises(exceptions.CommandError,
                          self._test_create_policy,
                          'name', 'description',
                          'action', 'listener',
                          action='REDIRECT_TO_POOL')

    def test_create_reject_policy_with_url(self):
        # lbaas-l7policy-create REJECT policy while specifying url argument.
        self.assertRaises(exceptions.CommandError,
                          self._test_create_policy,
                          'action', 'listener',
                          'redirect-url')

    def test_create_reject_policy_with_pool(self):
        # lbaas-l7policy-create REJECT policy while specifying pool argument.
        self.assertRaises(exceptions.CommandError,
                          self._test_create_policy,
                          'action', 'listener',
                          'redirect-pool')

    def test_create_pool_redirect_policy_with_url(self):
        # lbaas-l7policy-create REDIRECT_TO_POOL policy with url argument.
        self.assertRaises(exceptions.CommandError,
                          self._test_create_policy,
                          'action', 'listener',
                          'redirect-pool', 'redirect-url',
                          action='REDIRECT_TO_POOL')

    def test_create_url_redirect_policy_with_pool(self):
        # lbaas-l7policy-create REDIRECT_TO_URL policy with pool argument.
        self.assertRaises(exceptions.CommandError,
                          self._test_create_policy,
                          'action', 'listener',
                          'redirect-pool', 'redirect-url',
                          action='REDIRECT_TO_URL')

    def test_list_policies(self):
        # lbaas-l7policy-list.

        resources = 'l7policies'
        cmd_resources = 'lbaas_l7policies'
        cmd = l7policy.ListL7Policy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True,
                                  cmd_resources=cmd_resources)

    def test_list_policies_pagination(self):
        # lbaas-l7policy-list with pagination.

        resources = 'l7policies'
        cmd_resources = 'lbaas_l7policies'
        cmd = l7policy.ListL7Policy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(
            resources, cmd, cmd_resources=cmd_resources)

    def test_list_policies_sort(self):
        # lbaas-l7policy-list --sort-key id --sort-key asc.

        resources = 'l7policies'
        cmd_resources = 'lbaas_l7policies'
        cmd = l7policy.ListL7Policy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(
            resources, cmd, True, cmd_resources=cmd_resources)

    def test_list_policies_limit(self):
        # lbaas-l7policy-list -P.

        resources = 'l7policies'
        cmd_resources = 'lbaas_l7policies'
        cmd = l7policy.ListL7Policy(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(
            resources, cmd, page_size=1000, cmd_resources=cmd_resources)

    def test_show_policy_id(self):
        # lbaas-l7policy-show test_id.

        resource = 'l7policy'
        cmd_resource = 'lbaas_l7policy'
        cmd = l7policy.ShowL7Policy(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'test_id', self.test_id]
        self._test_show_resource(
            resource, cmd, self.test_id, args,
            ['test_id'], cmd_resource=cmd_resource)

    def test_show_policy_id_name(self):
        # lbaas-l7policy-show.

        resource = 'l7policy'
        cmd_resource = 'lbaas_l7policy'
        cmd = l7policy.ShowL7Policy(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'test_id', '--fields', 'name', self.test_id]
        self._test_show_resource(
            resource, cmd, self.test_id, args,
            ['test_id', 'name'], cmd_resource=cmd_resource)

    def test_disable_policy(self):
        # lbaas-l7policy-update test_id --admin-state-up False.

        self._test_update_policy('admin-state-up',
                                 **{'admin-state-up': 'False'})

    def test_update_policy_name_and_description(self):
        # lbaas-l7policy-update test_id --name other --description other_desc.

        self._test_update_policy('name', 'description',
                                 name='name',
                                 description='other desc')

    def test_update_pool_redirect_policy(self):
        # lbaas-l7policy-update test_id --action REDIRECT_TO_POOL
        #    --redirect-pool id.

        self._test_update_policy('action', 'redirect-pool',
                                 **{'action': 'REDIRECT_TO_POOL',
                                    'redirect-pool': 'id'})

    def test_update_url_redirect_policy(self):
        # lbaas-l7policy-update test_id --action REDIRECT_TO_URL
        #    --redirect-url http://other_url.

        self._test_update_policy('action', 'redirect-url',
                                 **{'action': 'REDIRECT_TO_URL',
                                    'redirect-url': 'http://other_url'})

    def test_update_policy_position(self):
        # lbaas-l7policy-update test_id --position 2.

        self._test_update_policy('position',
                                 position=2)

    def test_delete_policy(self):
        # lbaas-l7policy-delete test_id.

        resource = 'l7policy'
        cmd_resource = 'lbaas_l7policy'
        cmd = l7policy.DeleteL7Policy(test_cli20.MyApp(sys.stdout), None)
        test_id = 'test_id'
        args = [test_id]
        self._test_delete_resource(resource, cmd, test_id, args,
                                   cmd_resource=cmd_resource)
