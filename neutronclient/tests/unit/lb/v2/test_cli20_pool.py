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

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0.lb.v2 import pool
from neutronclient.tests.unit import test_cli20


class CLITestV20LbPoolJSON(test_cli20.CLITestV20Base):

    def test_create_pool_with_listener(self):
        # lbaas-pool-create with listener
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.CreatePool(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        lb_algorithm = 'ROUND_ROBIN'
        listener = 'listener'
        protocol = 'TCP'
        args = ['--lb-algorithm', lb_algorithm, '--protocol', protocol,
                '--listener', listener]
        position_names = ['admin_state_up', 'lb_algorithm', 'protocol',
                          'listener_id']
        position_values = [True, lb_algorithm, protocol, listener]
        self._test_create_resource(resource, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_create_pool_with_loadbalancer_no_listener(self):
        """lbaas-pool-create with loadbalancer, no listener."""
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.CreatePool(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        lb_algorithm = 'ROUND_ROBIN'
        loadbalancer = 'loadbalancer'
        protocol = 'TCP'
        args = ['--lb-algorithm', lb_algorithm, '--protocol', protocol,
                '--loadbalancer', loadbalancer]
        position_names = ['admin_state_up', 'lb_algorithm', 'protocol',
                          'loadbalancer_id']
        position_values = [True, lb_algorithm, protocol, loadbalancer]
        self._test_create_resource(resource, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_create_pool_with_no_listener_or_loadbalancer(self):
        """lbaas-pool-create with no listener or loadbalancer."""
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.CreatePool(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        lb_algorithm = 'ROUND_ROBIN'
        protocol = 'TCP'
        args = ['--lb-algorithm', lb_algorithm, '--protocol', protocol]
        position_names = ['admin_state_up', 'lb_algorithm', 'protocol']
        position_values = [True, lb_algorithm, protocol]
        self._test_create_resource(resource, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource,
                                   no_api_call=True,
                                   expected_exception=exceptions.CommandError)

    def test_create_pool_with_all_params(self):
        # lbaas-pool-create with all params set.
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.CreatePool(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        lb_algorithm = 'ROUND_ROBIN'
        listener = 'listener'
        loadbalancer = 'loadbalancer'
        protocol = 'TCP'
        description = 'description'
        session_persistence_str = 'type=APP_COOKIE,cookie_name=1234'
        session_persistence = {'type': 'APP_COOKIE',
                               'cookie_name': '1234'}
        name = 'my-pool'
        args = ['--lb-algorithm', lb_algorithm, '--protocol', protocol,
                '--description', description, '--session-persistence',
                session_persistence_str, '--admin-state-down', '--name', name,
                '--listener', listener, '--loadbalancer', loadbalancer]
        position_names = ['lb_algorithm', 'protocol', 'description',
                          'session_persistence', 'admin_state_up', 'name',
                          'listener_id', 'loadbalancer_id']
        position_values = [lb_algorithm, protocol, description,
                           session_persistence, False, name, listener,
                           loadbalancer]
        self._test_create_resource(resource, cmd, '', my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_list_pools(self):
        # lbaas-pool-list.
        resources = 'pools'
        cmd_resources = 'lbaas_pools'
        cmd = pool.ListPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True,
                                  cmd_resources=cmd_resources)

    def test_list_pools_pagination(self):
        # lbaas-pool-list with pagination.
        resources = 'pools'
        cmd_resources = 'lbaas_pools'
        cmd = pool.ListPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd,
                                                  cmd_resources=cmd_resources)

    def test_list_pools_sort(self):
        # lbaas-pool-list --sort-key id --sort-key asc.
        resources = 'pools'
        cmd_resources = 'lbaas_pools'
        cmd = pool.ListPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True,
                                  cmd_resources=cmd_resources)

    def test_list_pools_limit(self):
        # lbaas-pool-list -P.
        resources = 'pools'
        cmd_resources = 'lbaas_pools'
        cmd = pool.ListPool(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000,
                                  cmd_resources=cmd_resources)

    def test_show_pool_id(self):
        # lbaas-pool-show test_id.
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.ShowPool(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'],
                                 cmd_resource=cmd_resource)

    def test_show_pool_id_name(self):
        # lbaas-pool-show.
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.ShowPool(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'],
                                 cmd_resource=cmd_resource)

    def test_update_pool(self):
        # lbaas-pool-update myid --name newname --description SuperPool
        # --lb-algorithm SOURCE_IP --admin-state-up
        # --session-persistence type=dict,type=HTTP_COOKIE,cookie_name=pie

        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.UpdatePool(test_cli20.MyApp(sys.stdout), None)
        args = ['myid', '--name', 'newname',
                '--description', 'SuperPool', '--lb-algorithm', "SOURCE_IP",
                '--admin-state-up', 'True',
                '--session-persistence', 'type=dict,'
                'type=HTTP_COOKIE,cookie_name=pie']
        body = {'name': 'newname',
                "description": "SuperPool",
                "lb_algorithm": "SOURCE_IP",
                "admin_state_up": 'True',
                'session_persistence': {
                    'type': 'HTTP_COOKIE',
                    'cookie_name': 'pie',
                }, }
        self._test_update_resource(resource, cmd, 'myid', args, body,
                                   cmd_resource=cmd_resource)
        # lbaas-pool-update myid --name Name
        # --no-session-persistence

        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.UpdatePool(test_cli20.MyApp(sys.stdout), None)
        args = ['myid', '--name', 'Name', '--no-session-persistence']
        body = {'name': "Name",
                "session_persistence": None, }
        self._test_update_resource(resource, cmd, 'myid', args, body,
                                   cmd_resource=cmd_resource)

    def test_delete_pool(self):
        # lbaas-pool-delete my-id.
        resource = 'pool'
        cmd_resource = 'lbaas_pool'
        cmd = pool.DeletePool(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args,
                                   cmd_resource=cmd_resource)
