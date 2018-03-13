#!/usr/bin/env python
# Copyright (C) 2013 Yahoo! Inc.
# All Rights Reserved.
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

import sys

import mock

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0 import quota as test_quota
from neutronclient.tests.unit import test_cli20


class CLITestV20Quota(test_cli20.CLITestV20Base):
    def test_show_quota(self):
        resource = 'quota'
        cmd = test_quota.ShowQuota(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--tenant-id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args)

    def test_update_quota(self):
        resource = 'quota'
        cmd = test_quota.UpdateQuota(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--tenant-id', self.test_id, '--network', 'test']
        self.assertRaises(
            exceptions.CommandError, self._test_update_resource,
            resource, cmd, self.test_id, args=args,
            extrafields={'network': 'new'})

    def test_delete_quota_get_parser(self):
        cmd = test_cli20.MyApp(sys.stdout)
        test_quota.DeleteQuota(cmd, None).get_parser(cmd)

    def test_show_quota_positional(self):
        resource = 'quota'
        cmd = test_quota.ShowQuota(
            test_cli20.MyApp(sys.stdout), None)
        args = [self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args)

    def test_update_quota_positional(self):
        resource = 'quota'
        cmd = test_quota.UpdateQuota(
            test_cli20.MyApp(sys.stdout), None)
        args = [self.test_id, '--network', 'test']
        self.assertRaises(
            exceptions.CommandError, self._test_update_resource,
            resource, cmd, self.test_id, args=args,
            extrafields={'network': 'new'})

    def test_show_quota_default(self):
        resource = 'quota'
        cmd = test_quota.ShowQuotaDefault(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--tenant-id', self.test_id]
        expected_res = {'quota': {'port': 50, 'network': 10, 'subnet': 10}}
        resstr = self.client.serialize(expected_res)
        path = getattr(self.client, "quota_default_path")
        return_tup = (test_cli20.MyResp(200), resstr)
        with mock.patch.object(cmd, 'get_client',
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, 'request',
                                  return_value=return_tup) as mock_request:
            cmd_parser = cmd.get_parser("test_" + resource)
            parsed_args = cmd_parser.parse_args(args)
            cmd.run(parsed_args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.end_url(path % self.test_id), 'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        _str = self.fake_stdout.make_string()
        self.assertIn('network', _str)
        self.assertIn('subnet', _str)
        self.assertIn('port', _str)
        self.assertNotIn('subnetpool', _str)

    def test_update_quota_noargs(self):
        resource = 'quota'
        cmd = test_quota.UpdateQuota(test_cli20.MyApp(sys.stdout), None)
        args = [self.test_id]
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, self.test_id, args=args,
                          extrafields=None)
