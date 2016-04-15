# Copyright 2014 Blue Box Group, Inc.
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

from neutronclient.neutron.v2_0.lb.v2 import healthmonitor
from neutronclient.tests.unit import test_cli20


class CLITestV20LbHealthMonitorJSON(test_cli20.CLITestV20Base):

    def test_create_healthmonitor_with_mandatory_params(self):
        # lbaas-healthmonitor-create with mandatory params only.
        resource = 'healthmonitor'
        cmd_resource = 'lbaas_healthmonitor'
        cmd = healthmonitor.CreateHealthMonitor(test_cli20.MyApp(sys.stdout),
                                                None)
        my_id = 'my-id'
        type = 'PING'
        max_retries = '3'
        delay = '10'
        timeout = '60'
        pool = 'pool1'
        args = ['--type', type, '--max-retries', max_retries,
                '--delay', delay, '--timeout', timeout, '--pool', pool]
        position_names = ['type', 'max_retries', 'delay', 'timeout', 'pool_id']
        position_values = [type, max_retries, delay, timeout, pool]
        self._test_create_resource(resource, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_create_healthmonitor_with_all_params(self):
        # lbaas-healthmonitor-create with all params set.
        resource = 'healthmonitor'
        cmd_resource = 'lbaas_healthmonitor'
        cmd = healthmonitor.CreateHealthMonitor(test_cli20.MyApp(sys.stdout),
                                                None)
        my_id = 'my-id'
        type = 'PING'
        max_retries = '3'
        delay = '10'
        timeout = '60'
        http_method = 'GET'
        expected_codes = '201'
        url_path = '/somepath'
        pool = 'pool1'
        name = 'healthmonitor1'
        args = ['--admin-state-down', '--http-method', http_method,
                '--expected-codes', expected_codes, '--url-path', url_path,
                '--type', type, '--max-retries', max_retries,
                '--delay', delay, '--timeout', timeout, '--pool', pool,
                '--name', name]
        position_names = ['admin_state_up', 'http_method', 'expected_codes',
                          'url_path', 'type', 'max_retries', 'delay',
                          'timeout', 'pool_id', 'name']
        position_values = [False, http_method, expected_codes, url_path,
                           type, max_retries, delay, timeout, pool, name]
        self._test_create_resource(resource, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_list_healthmonitors(self):
        # lbaas-healthmonitor-list.
        resources = 'healthmonitors'
        cmd_resources = 'lbaas_healthmonitors'
        cmd = healthmonitor.ListHealthMonitor(test_cli20.MyApp(sys.stdout),
                                              None)
        self._test_list_resources(resources, cmd, True,
                                  cmd_resources=cmd_resources)

    def test_list_healthmonitors_pagination(self):
        # lbaas-healthmonitor-list with pagination.
        resources = 'healthmonitors'
        cmd_resources = 'lbaas_healthmonitors'
        cmd = healthmonitor.ListHealthMonitor(test_cli20.MyApp(sys.stdout),
                                              None)
        self._test_list_resources_with_pagination(resources, cmd,
                                                  cmd_resources=cmd_resources)

    def test_list_healthmonitors_sort(self):
        # lbaas-healthmonitor-list --sort-key id --sort-key asc.
        resources = 'healthmonitors'
        cmd_resources = 'lbaas_healthmonitors'
        cmd = healthmonitor.ListHealthMonitor(test_cli20.MyApp(sys.stdout),
                                              None)
        self._test_list_resources(resources, cmd, True,
                                  cmd_resources=cmd_resources)

    def test_list_healthmonitors_limit(self):
        # lbaas-healthmonitor-list -P.
        resources = 'healthmonitors'
        cmd_resources = 'lbaas_healthmonitors'
        cmd = healthmonitor.ListHealthMonitor(test_cli20.MyApp(sys.stdout),
                                              None)
        self._test_list_resources(resources, cmd, page_size=1000,
                                  cmd_resources=cmd_resources)

    def test_show_healthmonitor_id(self):
        # lbaas-healthmonitor-show test_id.
        resource = 'healthmonitor'
        cmd_resource = 'lbaas_healthmonitor'
        cmd = healthmonitor.ShowHealthMonitor(test_cli20.MyApp(sys.stdout),
                                              None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'],
                                 cmd_resource=cmd_resource)

    def test_show_healthmonitor_id_name(self):
        # lbaas-healthmonitor-show.
        resource = 'healthmonitor'
        cmd_resource = 'lbaas_healthmonitor'
        cmd = healthmonitor.ShowHealthMonitor(test_cli20.MyApp(sys.stdout),
                                              None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'],
                                 cmd_resource=cmd_resource)

    def _test_update_hm(self, args, expected_values):
        resource = 'healthmonitor'
        cmd_resource = 'lbaas_healthmonitor'
        my_id = 'myid'
        cmd = healthmonitor.UpdateHealthMonitor(test_cli20.MyApp(sys.stdout),
                                                None)
        args.insert(0, my_id)
        self._test_update_resource(resource, cmd, my_id,
                                   args,
                                   expected_values,
                                   cmd_resource=cmd_resource)

    def test_update_healthmonitor(self):
        # lbaas-healthmonitor-update myid --name newname.
        self._test_update_hm(['--name', 'newname'], {'name': 'newname', })
        # lbaas-healthmonitor-update myid --delay 10.
        self._test_update_hm(['--delay', '10'], {'delay': '10'})
        # lbaas-healthmonitor-update myid --timeout 5.
        self._test_update_hm(['--timeout', '5'], {'timeout': '5', })
        # lbaas-healthmonitor-update myid --delay 10.
        self._test_update_hm(['--http-method', 'OPTIONS'],
                             {'http_method': 'OPTIONS'})
        # lbaas-healthmonitor-update myid --url-path /test/string .
        self._test_update_hm(['--url-path', '/test/string'],
                             {'url_path': '/test/string', })
        # lbaas-healthmonitor-update myid --max-retries 5
        self._test_update_hm(['--max-retries', '5'], {'max_retries': '5'})
        # lbaas-healthmonitor-update myid --expected-codes 201
        self._test_update_hm(['--expected-codes', '201'],
                             {'expected_codes': '201'})
        # lbaas-healthmonitor-update myid --admin-state-up False
        self._test_update_hm(['--admin-state-up', 'False'],
                             {'admin_state_up': 'False'})

    def test_delete_healthmonitor(self):
        # lbaas-healthmonitor-delete my-id.
        resource = 'healthmonitor'
        cmd_resource = 'lbaas_healthmonitor'
        cmd = healthmonitor.DeleteHealthMonitor(test_cli20.MyApp(sys.stdout),
                                                None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args,
                                   cmd_resource=cmd_resource)
