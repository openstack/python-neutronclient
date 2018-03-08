# Copyright 2012 OpenStack Foundation.
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

import mock
from oslo_utils import uuidutils
import testtools

from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.tests.unit import test_cli20
from neutronclient.v2_0 import client


class CLITestNameorID(testtools.TestCase):

    def setUp(self):
        """Prepare the test environment."""
        super(CLITestNameorID, self).setUp()
        self.endurl = test_cli20.ENDURL
        self.client = client.Client(token=test_cli20.TOKEN,
                                    endpoint_url=self.endurl)

    def test_get_id_from_id(self):
        _id = uuidutils.generate_uuid()
        reses = {'networks': [{'id': _id, }, ], }
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        path = getattr(self.client, "networks_path")
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            returned_id = neutronV20.find_resourceid_by_name_or_id(
                self.client, 'network', _id)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, "fields=id&id=" + _id),
                self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        self.assertEqual(_id, returned_id)

    def test_get_id_from_id_then_name_empty(self):
        _id = uuidutils.generate_uuid()
        reses = {'networks': [{'id': _id, }, ], }
        resstr = self.client.serialize(reses)
        resstr1 = self.client.serialize({'networks': []})
        path = getattr(self.client, "networks_path")
        with mock.patch.object(self.client.httpclient,
                               "request") as mock_request:
            mock_request.side_effect = [(test_cli20.MyResp(200), resstr1),
                                        (test_cli20.MyResp(200), resstr)]
            returned_id = neutronV20.find_resourceid_by_name_or_id(
                self.client, 'network', _id)

        self.assertEqual(2, mock_request.call_count)
        mock_request.assert_has_calls([
            mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(path, "fields=id&id=" + _id),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN})),
            mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(path, "fields=id&name=" + _id),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN}))])
        self.assertEqual(_id, returned_id)

    def test_get_id_from_name(self):
        name = 'myname'
        _id = uuidutils.generate_uuid()
        reses = {'networks': [{'id': _id, }, ], }
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        path = getattr(self.client, "networks_path")
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            returned_id = neutronV20.find_resourceid_by_name_or_id(
                self.client, 'network', name)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, "fields=id&name=" + name),
                self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        self.assertEqual(_id, returned_id)

    def test_get_id_from_name_multiple(self):
        name = 'myname'
        reses = {'networks': [{'id': uuidutils.generate_uuid()},
                              {'id': uuidutils.generate_uuid()}]}
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        path = getattr(self.client, "networks_path")
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            exception = self.assertRaises(
                exceptions.NeutronClientNoUniqueMatch,
                neutronV20.find_resourceid_by_name_or_id,
                self.client, 'network', name)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, "fields=id&name=" + name),
                self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        self.assertIn('Multiple', exception.message)

    def test_get_id_from_name_notfound(self):
        name = 'myname'
        reses = {'networks': []}
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        path = getattr(self.client, "networks_path")
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            exception = self.assertRaises(
                exceptions.NotFound,
                neutronV20.find_resourceid_by_name_or_id,
                self.client, 'network', name)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, "fields=id&name=" + name),
                self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        self.assertIn('Unable to find', exception.message)
        self.assertEqual(404, exception.status_code)

    def test_get_id_from_name_multiple_with_project(self):
        name = 'web_server'
        project = uuidutils.generate_uuid()
        expect_id = uuidutils.generate_uuid()
        reses = {'security_groups':
                 [{'id': expect_id, 'tenant_id': project}]}
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        path = getattr(self.client, "security_groups_path")
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            observed_id = neutronV20.find_resourceid_by_name_or_id(
                self.client, 'security_group', name, project)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, "fields=id&name=%s&tenant_id=%s" %
                                         (name, project)), self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        self.assertEqual(expect_id, observed_id)

    def test_get_id_from_name_multiple_with_project_not_found(self):
        name = 'web_server'
        project = uuidutils.generate_uuid()
        resstr_notfound = self.client.serialize({'security_groups': []})
        resp = (test_cli20.MyResp(200), resstr_notfound)
        path = getattr(self.client, "security_groups_path")
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            exc = self.assertRaises(exceptions.NotFound,
                                    neutronV20.find_resourceid_by_name_or_id,
                                    self.client, 'security_group', name,
                                    project)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, "fields=id&name=%s&tenant_id=%s" %
                                         (name, project)), self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        self.assertIn('Unable to find', exc.message)
        self.assertEqual(404, exc.status_code)

    def _test_get_resource_by_id(self, id_only=False):
        _id = uuidutils.generate_uuid()
        net = {'id': _id, 'name': 'test'}
        reses = {'networks': [net], }
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        path = getattr(self.client, "networks_path")
        if id_only:
            query_params = "fields=id&id=%s" % _id
        else:
            query_params = "id=%s" % _id
        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            if id_only:
                returned_id = neutronV20.find_resourceid_by_id(
                    self.client, 'network', _id)
                self.assertEqual(_id, returned_id)
            else:
                result = neutronV20.find_resource_by_id(
                    self.client, 'network', _id)
                self.assertEqual(net, result)

        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, query_params),
                self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))

    def test_get_resource_by_id(self):
        self._test_get_resource_by_id(id_only=False)

    def test_get_resourceid_by_id(self):
        self._test_get_resource_by_id(id_only=True)
