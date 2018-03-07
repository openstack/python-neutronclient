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

import sys

import mock

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0 import network
from neutronclient.neutron.v2_0 import tag
from neutronclient import shell
from neutronclient.tests.unit import test_cli20


class CLITestV20Tag(test_cli20.CLITestV20Base):
    def _test_tag_operation(self, cmd, path, method, args, prog_name,
                            body=None):
        with mock.patch.object(cmd, 'get_client',
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, 'request',
                                  return_value=(test_cli20.MyResp(204), None)
                                  ) as mock_request:
            if body:
                body = test_cli20.MyComparator(body, self.client)
            cmd_parser = cmd.get_parser(prog_name)
            shell.run_command(cmd, cmd_parser, args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(test_cli20.end_url(path), self.client),
            method, body=body,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))

    def _test_tags_query(self, cmd, resources, args, query):
        path = getattr(self.client, resources + "_path")
        res = {resources: [{'id': 'myid'}]}
        resstr = self.client.serialize(res)
        with mock.patch.object(cmd, 'get_client',
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, 'request',
                                  return_value=(test_cli20.MyResp(200), resstr)
                                  ) as mock_request:
            cmd_parser = cmd.get_parser("list_networks")
            shell.run_command(cmd, cmd_parser, args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(test_cli20.end_url(path, query),
                                       self.client),
            'GET', body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))

        _str = self.fake_stdout.make_string()
        self.assertIn('myid', _str)

    def _make_tag_path(self, resource, resource_id, tag):
        path = getattr(self.client, "tag_path")
        resource_plural = self.client.get_resource_plural(resource)
        return path % (resource_plural, resource_id, tag)

    def _make_tags_path(self, resource, resource_id):
        path = getattr(self.client, "tags_path")
        resource_plural = self.client.get_resource_plural(resource)
        return path % (resource_plural, resource_id)

    def test_add_tag(self):
        cmd = tag.AddTag(test_cli20.MyApp(sys.stdout), None)
        path = self._make_tag_path('network', 'myid', 'red')
        args = ['--resource-type', 'network', '--resource', 'myid',
                '--tag', 'red']
        self._test_tag_operation(cmd, path, 'PUT', args, "tag-add")

    def test_add_tag_empty_tag(self):
        cmd = tag.AddTag(test_cli20.MyApp(sys.stdout), None)
        path = self._make_tag_path('network', 'myid', '')
        args = ['--resource-type', 'network', '--resource', 'myid',
                '--tag', '']
        self.assertRaises(exceptions.CommandError, self._test_tag_operation,
                          cmd, path, 'PUT', args, "tag-add")

    def test_replace_tag(self):
        cmd = tag.ReplaceTag(test_cli20.MyApp(sys.stdout), None)
        path = self._make_tags_path('network', 'myid')
        args = ['--resource-type', 'network', '--resource', 'myid',
                '--tag', 'red', '--tag', 'blue']
        body = {'tags': ['red', 'blue']}
        self._test_tag_operation(cmd, path, 'PUT', args, "tag-replace",
                                 body=body)

    def test_remove_tag(self):
        cmd = tag.RemoveTag(test_cli20.MyApp(sys.stdout), None)
        path = self._make_tag_path('network', 'myid', 'red')
        args = ['--resource-type', 'network', '--resource', 'myid',
                '--tag', 'red']
        self._test_tag_operation(cmd, path, 'DELETE', args, "tag-remove")

    def test_remove_tag_all(self):
        cmd = tag.RemoveTag(test_cli20.MyApp(sys.stdout), None)
        path = self._make_tags_path('network', 'myid')
        args = ['--resource-type', 'network', '--resource', 'myid',
                '--all']
        self._test_tag_operation(cmd, path, 'DELETE', args, "tag-remove")

    def test_no_tag_nor_all(self):
        cmd = tag.RemoveTag(test_cli20.MyApp(sys.stdout), None)
        path = self._make_tags_path('network', 'myid')
        args = ['--resource-type', 'network', '--resource', 'myid']
        self.assertRaises(exceptions.CommandError, self._test_tag_operation,
                          cmd, path, 'DELETE', args, "tag-remove")

    def test_tags_query(self):
        # This test examines that '-' in the tag related filters
        # is not converted to '_'.
        resources = 'networks'
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        with mock.patch.object(network.ListNetwork, 'extend_list'):
            args = ['--not-tags', 'red,blue', '--tags-any', 'green',
                    '--not-tags-any', 'black']
            query = "not-tags=red,blue&tags-any=green&not-tags-any=black"
            self._test_tags_query(cmd, resources, args, query)
