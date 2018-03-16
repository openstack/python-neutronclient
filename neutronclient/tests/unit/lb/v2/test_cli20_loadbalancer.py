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

import mock

from neutronclient.neutron.v2_0.lb.v2 import loadbalancer as lb
from neutronclient.tests.unit import test_cli20


class CLITestV20LbLoadBalancerJSON(test_cli20.CLITestV20Base):

    def test_create_loadbalancer_with_mandatory_params(self):
        # lbaas-loadbalancer-create with mandatory params only.
        resource = 'loadbalancer'
        cmd_resource = 'lbaas_loadbalancer'
        cmd = lb.CreateLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        name = 'lbaas-loadbalancer-name'
        vip_subnet_id = 'vip-subnet'
        my_id = 'my-id'
        args = [vip_subnet_id]
        position_names = ['vip_subnet_id']
        position_values = [vip_subnet_id]
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_create_loadbalancer_with_all_params(self):
        # lbaas-loadbalancer-create with all params set.
        resource = 'loadbalancer'
        cmd_resource = 'lbaas_loadbalancer'
        cmd = lb.CreateLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        name = 'lbaas-loadbalancer-name'
        description = 'lbaas-loadbalancer-desc'
        flavor_id = 'lbaas-loadbalancer-flavor'
        vip_subnet_id = 'vip-subnet'
        my_id = 'my-id'
        args = ['--admin-state-down', '--description', description,
                '--name', name, '--flavor', flavor_id, vip_subnet_id]
        position_names = ['admin_state_up', 'description', 'name',
                          'flavor_id', 'vip_subnet_id']
        position_values = [False, description, name, flavor_id, vip_subnet_id]
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values,
                                   cmd_resource=cmd_resource)

    def test_list_loadbalancers(self):
        # lbaas-loadbalancer-list.
        resources = 'loadbalancers'
        cmd_resources = 'lbaas_loadbalancers'
        cmd = lb.ListLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True,
                                  cmd_resources=cmd_resources)

    def test_list_loadbalancers_pagination(self):
        # lbaas-loadbalancer-list with pagination.
        resources = 'loadbalancers'
        cmd_resources = 'lbaas_loadbalancers'
        cmd = lb.ListLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd,
                                                  cmd_resources=cmd_resources)

    def test_list_loadbalancers_sort(self):
        # lbaas-loadbalancer-list --sort-key name --sort-key id --sort-key asc
        # --sort-key desc
        resources = 'loadbalancers'
        cmd_resources = 'lbaas_loadbalancers'
        cmd = lb.ListLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"],
                                  cmd_resources=cmd_resources)

    def test_list_loadbalancers_limit(self):
        # lbaas-loadbalancer-list -P.
        resources = 'loadbalancers'
        cmd_resources = 'lbaas_loadbalancers'
        cmd = lb.ListLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000,
                                  cmd_resources=cmd_resources)

    def test_show_loadbalancer_id(self):
        # lbaas-loadbalancer-loadbalancer-show test_id.
        resource = 'loadbalancer'
        cmd_resource = 'lbaas_loadbalancer'
        cmd = lb.ShowLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'],
                                 cmd_resource=cmd_resource)

    def test_show_loadbalancer_id_name(self):
        # lbaas-loadbalancer-loadbalancer-show.
        resource = 'loadbalancer'
        cmd_resource = 'lbaas_loadbalancer'
        cmd = lb.ShowLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'],
                                 cmd_resource=cmd_resource)

    def _test_update_lb(self, args, expected_values):
        resource = 'loadbalancer'
        cmd_resource = 'lbaas_loadbalancer'
        my_id = 'myid'
        args.insert(0, my_id)
        cmd = lb.UpdateLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, my_id,
                                   args, expected_values,
                                   cmd_resource=cmd_resource)

    def test_update_loadbalancer(self):
        # lbaas-loadbalancer-update myid --name newname.
        self._test_update_lb(['--name', 'newname'], {'name': 'newname', })
        # lbaas-loadbalancer-update myid --description check.
        self._test_update_lb(['--description', 'check'],
                             {'description': 'check', })
        # lbaas-loadbalancer-update myid --admin-state-up False.
        self._test_update_lb(['--admin-state-up', 'False'],
                             {'admin_state_up': 'False', })

    def test_delete_loadbalancer(self):
        # lbaas-loadbalancer-loadbalancer-delete my-id.
        resource = 'loadbalancer'
        cmd_resource = 'lbaas_loadbalancer'
        cmd = lb.DeleteLoadBalancer(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args,
                                   cmd_resource=cmd_resource)

    def test_retrieve_loadbalancer_stats(self):
        # lbaas-loadbalancer-stats test_id.
        resource = 'loadbalancer'
        cmd = lb.RetrieveLoadBalancerStats(test_cli20.MyApp(sys.stdout), None)
        my_id = self.test_id
        fields = ['bytes_in', 'bytes_out']
        args = ['--fields', 'bytes_in', '--fields', 'bytes_out', my_id]

        query = "&".join(["fields=%s" % field for field in fields])
        expected_res = {'stats': {'bytes_in': '1234', 'bytes_out': '4321'}}
        resstr = self.client.serialize(expected_res)
        path = getattr(self.client, "lbaas_loadbalancer_path_stats")
        return_tup = (test_cli20.MyResp(200), resstr)

        cmd_parser = cmd.get_parser("test_" + resource)
        parsed_args = cmd_parser.parse_args(args)
        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=return_tup) as mock_request:
            cmd.run(parsed_args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), 2)
        mock_request.assert_called_once_with(
            test_cli20.end_url(path % my_id, query), 'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        _str = self.fake_stdout.make_string()
        self.assertIn('bytes_in', _str)
        self.assertIn('1234', _str)
        self.assertIn('bytes_out', _str)
        self.assertIn('4321', _str)

    def test_get_loadbalancer_statuses(self):
        # lbaas-loadbalancer-status test_id.
        resource = 'loadbalancer'
        cmd = lb.RetrieveLoadBalancerStatus(test_cli20.MyApp(sys.stdout), None)
        my_id = self.test_id
        args = [my_id]

        expected_res = {'statuses': {'operating_status': 'ONLINE',
                                     'provisioning_status': 'ACTIVE'}}

        resstr = self.client.serialize(expected_res)

        path = getattr(self.client, "lbaas_loadbalancer_path_status")
        return_tup = (test_cli20.MyResp(200), resstr)

        cmd_parser = cmd.get_parser("test_" + resource)
        parsed_args = cmd_parser.parse_args(args)
        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=return_tup) as mock_request:
            cmd.run(parsed_args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.end_url(path % my_id), 'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        _str = self.fake_stdout.make_string()
        self.assertIn('operating_status', _str)
        self.assertIn('ONLINE', _str)
        self.assertIn('provisioning_status', _str)
        self.assertIn('ACTIVE', _str)
