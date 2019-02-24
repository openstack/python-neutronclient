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

import contextlib
import itertools
import sys

import mock
from oslo_serialization import jsonutils
from oslo_utils import encodeutils
from oslotest import base
import requests
import six
import six.moves.urllib.parse as urlparse
import yaml

from neutronclient.common import constants
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV2_0
from neutronclient.neutron.v2_0 import network
from neutronclient import shell
from neutronclient.v2_0 import client

API_VERSION = "2.0"
TOKEN = 'testtoken'
ENDURL = 'localurl'
REQUEST_ID = 'test_request_id'


@contextlib.contextmanager
def capture_std_streams():
    fake_stdout, fake_stderr = six.StringIO(), six.StringIO()
    stdout, stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = fake_stdout, fake_stderr
        yield fake_stdout, fake_stderr
    finally:
        sys.stdout, sys.stderr = stdout, stderr


class FakeStdout(object):

    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result += encodeutils.safe_decode(line, 'utf-8')
        return result


class MyRequest(requests.Request):
    def __init__(self, method=None):
        self.method = method


class MyResp(requests.Response):
    def __init__(self, status_code, headers=None, reason=None,
                 request=None, url=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.reason = reason
        self.request = request or MyRequest()
        self.url = url


class MyApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout


def end_url(path, query=None):
    _url_str = ENDURL + "/v" + API_VERSION + path
    return query and _url_str + "?" + query or _url_str


class MyUrlComparator(object):
    def __init__(self, lhs, client):
        self.lhs = lhs
        self.client = client

    def __eq__(self, rhs):
        lhsp = urlparse.urlparse(self.lhs)
        rhsp = urlparse.urlparse(rhs)

        lhs_qs = urlparse.parse_qsl(lhsp.query)
        rhs_qs = urlparse.parse_qsl(rhsp.query)

        return (lhsp.scheme == rhsp.scheme and
                lhsp.netloc == rhsp.netloc and
                lhsp.path == rhsp.path and
                len(lhs_qs) == len(rhs_qs) and
                set(lhs_qs) == set(rhs_qs))

    def __str__(self):
        return self.lhs

    def __repr__(self):
        return str(self)


class MyComparator(object):
    def __init__(self, lhs, client):
        self.lhs = lhs
        self.client = client

    def _com_dict(self, lhs, rhs):
        if len(lhs) != len(rhs):
            return False
        for key, value in six.iteritems(lhs):
            if key not in rhs:
                return False
            rhs_value = rhs[key]
            if not self._com(value, rhs_value):
                return False
        return True

    def _com_list(self, lhs, rhs):
        if len(lhs) != len(rhs):
            return False
        for lhs_value in lhs:
            if lhs_value not in rhs:
                return False
        return True

    def _com(self, lhs, rhs):
        if lhs is None:
            return rhs is None
        if isinstance(lhs, dict):
            if not isinstance(rhs, dict):
                return False
            return self._com_dict(lhs, rhs)
        if isinstance(lhs, list):
            if not isinstance(rhs, list):
                return False
            return self._com_list(lhs, rhs)
        if isinstance(lhs, tuple):
            if not isinstance(rhs, tuple):
                return False
            return self._com_list(lhs, rhs)
        return lhs == rhs

    def __eq__(self, rhs):
        if self.client:
            rhs = self.client.deserialize(rhs, 200)
        return self._com(self.lhs, rhs)

    def __repr__(self):
        if self.client:
            return self.client.serialize(self.lhs)
        return str(self.lhs)


class ContainsKeyValue(object):
    """Checks whether key/value pair(s) are included in a dict parameter.

    This class just checks whether specifid key/value pairs passed in
    __init__() are included in a dict parameter. The comparison does not
    fail even if other key/value pair(s) exists in a target dict.
    """

    def __init__(self, expected):
        self._expected = expected

    def __eq__(self, other):
        if not isinstance(other, dict):
            return False
        for key, value in self._expected.items():
            if key not in other:
                return False
            if other[key] != value:
                return False
        return True

    def __repr__(self):
        return ('<%s (expected: %s)>' %
                (self.__class__.__name__, self._expected))


class IsA(object):
    """Checks whether the parameter is of specific type."""

    def __init__(self, expected_type):
        self._expected_type = expected_type

    def __eq__(self, other):
        return isinstance(other, self._expected_type)

    def __repr__(self):
        return ('<%s (expected: %s)>' %
                (self.__class__.__name__, self._expected_type))


class CLITestV20Base(base.BaseTestCase):

    test_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    id_field = 'id'

    non_admin_status_resources = []

    def _find_resourceid(self, client, resource, name_or_id,
                         cmd_resource=None, parent_id=None):
        return name_or_id

    def setUp(self, plurals=None):
        """Prepare the test environment."""
        super(CLITestV20Base, self).setUp()
        client.Client.EXTED_PLURALS.update(constants.PLURALS)
        if plurals is not None:
            client.Client.EXTED_PLURALS.update(plurals)
        self.metadata = {'plurals': client.Client.EXTED_PLURALS}
        self.endurl = ENDURL
        self.fake_stdout = FakeStdout()

        self.addCleanup(mock.patch.stopall)
        mock.patch('sys.stdout', new=self.fake_stdout).start()
        mock.patch('neutronclient.neutron.v2_0.find_resourceid_by_name_or_id',
                   new=self._find_resourceid).start()
        mock.patch('neutronclient.neutron.v2_0.find_resourceid_by_id',
                   new=self._find_resourceid).start()

        self.client = client.Client(token=TOKEN, endpoint_url=self.endurl)

    def register_non_admin_status_resource(self, resource_name):
        # TODO(amotoki):
        # It is recommended to define
        # "non_admin_status_resources in each test class rather than
        # using register_non_admin_status_resource method.

        # If we change self.non_admin_status_resources like this,
        # we need to ensure this should be an instance variable
        # to avoid changing the class variable.
        if (id(self.non_admin_status_resources) ==
                id(self.__class__.non_admin_status_resources)):
            self.non_admin_status_resources = (self.__class__.
                                               non_admin_status_resources[:])
        self.non_admin_status_resources.append(resource_name)

    def _test_create_resource(self, resource, cmd, name, myid, args,
                              position_names, position_values,
                              tenant_id=None, tags=None, admin_state_up=True,
                              extra_body=None, cmd_resource=None,
                              parent_id=None, no_api_call=False,
                              expected_exception=None,
                              **kwargs):
        if not cmd_resource:
            cmd_resource = resource
        if (resource in self.non_admin_status_resources):
            body = {resource: {}, }
        else:
            body = {resource: {'admin_state_up': admin_state_up, }, }
        if tenant_id:
            body[resource].update({'tenant_id': tenant_id})
        if tags:
            body[resource].update({'tags': tags})
        if extra_body:
            body[resource].update(extra_body)
        body[resource].update(kwargs)

        for i in range(len(position_names)):
            body[resource].update({position_names[i]: position_values[i]})
        ress = {resource:
                {self.id_field: myid}, }
        if name:
            ress[resource].update({'name': name})
        resstr = self.client.serialize(ress)
        # url method body
        resource_plural = self.client.get_resource_plural(cmd_resource)
        path = getattr(self.client, resource_plural + "_path")
        if parent_id:
            path = path % parent_id
        mock_body = MyComparator(body, self.client)

        cmd_parser = cmd.get_parser('create_' + resource)
        resp = (MyResp(200), resstr)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            if expected_exception:
                self.assertRaises(expected_exception,
                                  shell.run_command, cmd, cmd_parser, args)
            else:
                shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        if not no_api_call:
            mock_request.assert_called_once_with(
                end_url(path), 'POST',
                body=mock_body,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))
        if not expected_exception:
            _str = self.fake_stdout.make_string()
            self.assertIn(myid, _str)
            if name:
                self.assertIn(name, _str)

    def _test_list_columns(self, cmd, resources,
                           resources_out, args=('-f', 'json'),
                           cmd_resources=None, parent_id=None):
        if not cmd_resources:
            cmd_resources = resources

        resstr = self.client.serialize(resources_out)

        path = getattr(self.client, cmd_resources + "_path")
        if parent_id:
            path = path % parent_id
        cmd_parser = cmd.get_parser("list_" + cmd_resources)
        resp = (MyResp(200), resstr)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_called_once_with(
            end_url(path), 'GET',
            body=None,
            headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))

    def _test_list_resources(self, resources, cmd, detail=False, tags=(),
                             fields_1=(), fields_2=(), page_size=None,
                             sort_key=(), sort_dir=(), response_contents=None,
                             base_args=None, path=None, cmd_resources=None,
                             parent_id=None, output_format=None, query=""):
        if not cmd_resources:
            cmd_resources = resources
        if response_contents is None:
            contents = [{self.id_field: 'myid1', },
                        {self.id_field: 'myid2', }, ]
        else:
            contents = response_contents
        reses = {resources: contents}
        resstr = self.client.serialize(reses)
        # url method body
        args = base_args if base_args is not None else []
        if detail:
            args.append('-D')
        if fields_1:
            for field in fields_1:
                args.append('--fields')
                args.append(field)

        if tags:
            args.append('--')
            args.append("--tag")
        for tag in tags:
            args.append(tag)
            tag_query = urlparse.urlencode(
                {'tag': encodeutils.safe_encode(tag)})
            if query:
                query += "&" + tag_query
            else:
                query = tag_query
        if (not tags) and fields_2:
            args.append('--')
        if fields_2:
            args.append("--fields")
            for field in fields_2:
                args.append(field)
        if detail:
            query = query and query + '&verbose=True' or 'verbose=True'
        for field in itertools.chain(fields_1, fields_2):
            if query:
                query += "&fields=" + field
            else:
                query = "fields=" + field
        if page_size:
            args.append("--page-size")
            args.append(str(page_size))
            if query:
                query += "&limit=%s" % page_size
            else:
                query = "limit=%s" % page_size
        if sort_key:
            for key in sort_key:
                args.append('--sort-key')
                args.append(key)
                if query:
                    query += '&'
                query += 'sort_key=%s' % key
        if sort_dir:
            len_diff = len(sort_key) - len(sort_dir)
            if len_diff > 0:
                sort_dir = tuple(sort_dir) + ('asc',) * len_diff
            elif len_diff < 0:
                sort_dir = sort_dir[:len(sort_key)]
            for dir in sort_dir:
                args.append('--sort-dir')
                args.append(dir)
                if query:
                    query += '&'
                query += 'sort_dir=%s' % dir
        if path is None:
            path = getattr(self.client, cmd_resources + "_path")
            if parent_id:
                path = path % parent_id
        if output_format:
            args.append('-f')
            args.append(output_format)
        cmd_parser = cmd.get_parser("list_" + cmd_resources)
        resp = (MyResp(200), resstr)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_called_once_with(
            MyUrlComparator(end_url(path, query), self.client),
            'GET',
            body=None,
            headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))
        _str = self.fake_stdout.make_string()
        if response_contents is None:
            self.assertIn('myid1', _str)
        return _str

    def _test_list_resources_with_pagination(self, resources, cmd,
                                             base_args=None,
                                             cmd_resources=None,
                                             parent_id=None, query=""):
        if not cmd_resources:
            cmd_resources = resources

        path = getattr(self.client, cmd_resources + "_path")
        if parent_id:
            path = path % parent_id
        fake_query = "marker=myid2&limit=2"
        reses1 = {resources: [{'id': 'myid1', },
                              {'id': 'myid2', }],
                  '%s_links' % resources: [{'href': end_url(path, fake_query),
                                            'rel': 'next'}]}
        reses2 = {resources: [{'id': 'myid3', },
                              {'id': 'myid4', }]}
        resstr1 = self.client.serialize(reses1)
        resstr2 = self.client.serialize(reses2)
        cmd_parser = cmd.get_parser("list_" + cmd_resources)
        args = base_args if base_args is not None else []
        mock_request_calls = [
            mock.call(
                end_url(path, query), 'GET',
                body=None,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN})),
            mock.call(
                MyUrlComparator(end_url(path, fake_query),
                                self.client), 'GET',
                body=None,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))]
        mock_request_resp = [(MyResp(200), resstr1), (MyResp(200), resstr2)]

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient,
                                  "request") as mock_request:
            mock_request.side_effect = mock_request_resp
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        self.assertEqual(2, mock_request.call_count)
        mock_request.assert_has_calls(mock_request_calls)

    def _test_update_resource(self, resource, cmd, myid, args, extrafields,
                              cmd_resource=None, parent_id=None):
        if not cmd_resource:
            cmd_resource = resource

        body = {resource: extrafields}
        path = getattr(self.client, cmd_resource + "_path")
        if parent_id:
            path = path % (parent_id, myid)
        else:
            path = path % myid
        mock_body = MyComparator(body, self.client)

        cmd_parser = cmd.get_parser("update_" + cmd_resource)
        resp = (MyResp(204), None)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_called_once_with(
            MyUrlComparator(end_url(path), self.client),
            'PUT',
            body=mock_body,
            headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))
        _str = self.fake_stdout.make_string()
        self.assertIn(myid, _str)

    def _test_show_resource(self, resource, cmd, myid, args, fields=(),
                            cmd_resource=None, parent_id=None):
        if not cmd_resource:
            cmd_resource = resource

        query = "&".join(["fields=%s" % field for field in fields])
        expected_res = {resource:
                        {self.id_field: myid,
                         'name': 'myname', }, }
        resstr = self.client.serialize(expected_res)
        path = getattr(self.client, cmd_resource + "_path")
        if parent_id:
            path = path % (parent_id, myid)
        else:
            path = path % myid
        cmd_parser = cmd.get_parser("show_" + cmd_resource)
        resp = (MyResp(200), resstr)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_called_once_with(
            end_url(path, query), 'GET',
            body=None,
            headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))
        _str = self.fake_stdout.make_string()
        self.assertIn(myid, _str)
        self.assertIn('myname', _str)

    def _test_set_path_and_delete(self, path, parent_id, myid,
                                  mock_request_calls, mock_request_returns,
                                  delete_fail=False):
        return_val = 404 if delete_fail else 204
        if parent_id:
            path = path % (parent_id, myid)
        else:
            path = path % (myid)
        mock_request_returns.append((MyResp(return_val), None))
        mock_request_calls.append(mock.call(
            end_url(path), 'DELETE',
            body=None,
            headers=ContainsKeyValue({'X-Auth-Token': TOKEN})))

    def _test_delete_resource(self, resource, cmd, myid, args,
                              cmd_resource=None, parent_id=None,
                              extra_id=None, delete_fail=False):
        mock_request_calls = []
        mock_request_returns = []
        if not cmd_resource:
            cmd_resource = resource
        path = getattr(self.client, cmd_resource + "_path")
        self._test_set_path_and_delete(path, parent_id, myid,
                                       mock_request_calls,
                                       mock_request_returns)
        # extra_id is used to test for bulk_delete
        if extra_id:
            self._test_set_path_and_delete(path, parent_id, extra_id,
                                           mock_request_calls,
                                           mock_request_returns,
                                           delete_fail)
        cmd_parser = cmd.get_parser("delete_" + cmd_resource)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient,
                                  "request") as mock_request:
            mock_request.side_effect = mock_request_returns
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_has_calls(mock_request_calls)
        _str = self.fake_stdout.make_string()
        self.assertIn(myid, _str)
        if extra_id:
            self.assertIn(extra_id, _str)

    def _test_update_resource_action(self, resource, cmd, myid, action, args,
                                     body, expected_code=200, retval=None,
                                     cmd_resource=None):
        if not cmd_resource:
            cmd_resource = resource
        path = getattr(self.client, cmd_resource + "_path")
        path_action = '%s/%s' % (myid, action)
        cmd_parser = cmd.get_parser("update_" + cmd_resource)
        resp = (MyResp(expected_code), retval)

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request:
            shell.run_command(cmd, cmd_parser, args)

        self.assert_mock_multiple_calls_with_same_arguments(
            mock_get_client, mock.call(), None)
        mock_request.assert_called_once_with(
            end_url(path % path_action), 'PUT',
            body=MyComparator(body, self.client),
            headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))
        _str = self.fake_stdout.make_string()
        self.assertIn(myid, _str)

    def assert_mock_multiple_calls_with_same_arguments(
            self, mocked_method, expected_call, count):
        if count is None:
            self.assertLessEqual(1, mocked_method.call_count)
        else:
            self.assertEqual(count, mocked_method.call_count)
        mocked_method.assert_has_calls(
            [expected_call] * mocked_method.call_count)


class TestListCommand(neutronV2_0.ListCommand):
    resource = 'test_resource'
    filter_attrs = [
        'name',
        'admin_state_up',
        {'name': 'foo', 'help': 'non-boolean attribute foo'},
        {'name': 'bar', 'help': 'boolean attribute bar',
         'boolean': True},
        {'name': 'baz', 'help': 'integer attribute baz',
         'argparse_kwargs': {'choices': ['baz1', 'baz2']}},
    ]


class ListCommandTestCase(CLITestV20Base):

    def setUp(self):
        super(ListCommandTestCase, self).setUp()
        self.client.extend_list('test_resources', '/test_resources', None)
        setattr(self.client, 'test_resources_path', '/test_resources')

    def _test_list_resources_filter_params(self, base_args='', query=''):
        resources = 'test_resources'
        cmd = TestListCommand(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  base_args=base_args.split(),
                                  query=query)

    def _test_list_resources_with_arg_error(self, base_args=''):
        resources = 'test_resources'
        cmd = TestListCommand(MyApp(sys.stdout), None)
        # argparse parse error leads to SystemExit
        self.assertRaises(SystemExit,
                          self._test_list_resources,
                          resources, cmd,
                          base_args=base_args.split())

    def test_list_resources_without_filter(self):
        self._test_list_resources_filter_params()

    def test_list_resources_use_default_filter(self):
        self._test_list_resources_filter_params(
            base_args='--name val1 --admin-state-up False',
            query='name=val1&admin_state_up=False')

    def test_list_resources_use_custom_filter(self):
        self._test_list_resources_filter_params(
            base_args='--foo FOO --bar True',
            query='foo=FOO&bar=True')

    def test_list_resources_boolean_check_default_filter(self):
        self._test_list_resources_filter_params(
            base_args='--admin-state-up True', query='admin_state_up=True')
        self._test_list_resources_filter_params(
            base_args='--admin-state-up False', query='admin_state_up=False')
        self._test_list_resources_with_arg_error(
            base_args='--admin-state-up non-true-false')

    def test_list_resources_boolean_check_custom_filter(self):
        self._test_list_resources_filter_params(
            base_args='--bar True', query='bar=True')
        self._test_list_resources_filter_params(
            base_args='--bar False', query='bar=False')
        self._test_list_resources_with_arg_error(
            base_args='--bar non-true-false')

    def test_list_resources_argparse_kwargs(self):
        self._test_list_resources_filter_params(
            base_args='--baz baz1', query='baz=baz1')
        self._test_list_resources_filter_params(
            base_args='--baz baz2', query='baz=baz2')
        self._test_list_resources_with_arg_error(
            base_args='--bar non-choice')


class ClientV2TestJson(CLITestV20Base):
    def test_do_request_unicode(self):
        unicode_text = u'\u7f51\u7edc'
        # url with unicode
        action = u'/test'
        expected_action = action
        # query string with unicode
        params = {'test': unicode_text}
        expect_query = urlparse.urlencode(utils.safe_encode_dict(params))
        # request body with unicode
        body = params
        expect_body = self.client.serialize(body)
        self.client.httpclient.auth_token = encodeutils.safe_encode(
            unicode_text)
        expected_auth_token = encodeutils.safe_encode(unicode_text)
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = (MyResp(200, resp_headers), expect_body)

        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            result = self.client.do_request('PUT', action, body=body,
                                            params=params)

        mock_request.assert_called_once_with(
            end_url(expected_action, query=expect_query),
            'PUT', body=expect_body,
            headers=ContainsKeyValue({'X-Auth-Token': expected_auth_token}))
        # test response with unicode
        self.assertEqual(body, result)

    def test_do_request_error_without_response_body(self):
        params = {'test': 'value'}
        expect_query = six.moves.urllib.parse.urlencode(params)
        self.client.httpclient.auth_token = 'token'
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = (MyResp(400, headers=resp_headers, reason='An error'), '')

        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            error = self.assertRaises(exceptions.NeutronClientException,
                                      self.client.do_request, 'PUT', '/test',
                                      body='', params=params)

        mock_request.assert_called_once_with(
            MyUrlComparator(end_url('/test', query=expect_query), self.client),
            'PUT', body='',
            headers=ContainsKeyValue({'X-Auth-Token': 'token'}))
        expected_error = "An error\nNeutron server returns " \
                         "request_ids: %s" % [REQUEST_ID]
        self.assertEqual(expected_error, str(error))

    def test_do_request_with_long_uri_exception(self):
        long_string = 'x' * 8200                  # 8200 > MAX_URI_LEN:8192
        params = {'id': long_string}
        exception = self.assertRaises(exceptions.RequestURITooLong,
                                      self.client.do_request,
                                      'GET', '/test', body='', params=params)
        self.assertNotEqual(0, exception.excess)

    def test_do_request_request_ids(self):
        params = {'test': 'value'}
        expect_query = six.moves.urllib.parse.urlencode(params)
        self.client.httpclient.auth_token = 'token'
        body = params
        expect_body = self.client.serialize(body)
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = (MyResp(200, resp_headers), expect_body)

        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            result = self.client.do_request('PUT', '/test', body=body,
                                            params=params)

        mock_request.assert_called_once_with(
            MyUrlComparator(end_url('/test', query=expect_query), self.client),
            'PUT', body=expect_body,
            headers=ContainsKeyValue({'X-Auth-Token': 'token'}))

        self.assertEqual(body, result)
        self.assertEqual([REQUEST_ID], result.request_ids)

    def test_list_request_ids_with_retrieve_all_true(self):
        path = '/test'
        resources = 'tests'
        fake_query = "marker=myid2&limit=2"
        reses1 = {resources: [{'id': 'myid1', },
                              {'id': 'myid2', }],
                  '%s_links' % resources: [{'href': end_url(path, fake_query),
                                            'rel': 'next'}]}
        reses2 = {resources: [{'id': 'myid3', },
                              {'id': 'myid4', }]}
        resstr1 = self.client.serialize(reses1)
        resstr2 = self.client.serialize(reses2)
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = [(MyResp(200, resp_headers), resstr1),
                (MyResp(200, resp_headers), resstr2)]
        with mock.patch.object(self.client.httpclient, "request",
                               side_effect=resp) as mock_request:
            result = self.client.list(resources, path)

        self.assertEqual(2, mock_request.call_count)
        mock_request.assert_has_calls([
            mock.call(
                end_url(path, ""), 'GET',
                body=None,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN})),
            mock.call(
                MyUrlComparator(end_url(path, fake_query),
                                self.client), 'GET',
                body=None,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))])

        self.assertEqual([REQUEST_ID, REQUEST_ID], result.request_ids)

    def test_list_request_ids_with_retrieve_all_false(self):
        path = '/test'
        resources = 'tests'
        fake_query = "marker=myid2&limit=2"
        reses1 = {resources: [{'id': 'myid1', },
                              {'id': 'myid2', }],
                  '%s_links' % resources: [{'href': end_url(path, fake_query),
                                            'rel': 'next'}]}
        reses2 = {resources: [{'id': 'myid3', },
                              {'id': 'myid4', }]}
        resstr1 = self.client.serialize(reses1)
        resstr2 = self.client.serialize(reses2)
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = [(MyResp(200, resp_headers), resstr1),
                (MyResp(200, resp_headers), resstr2)]
        with mock.patch.object(self.client.httpclient, "request",
                               side_effect=resp) as mock_request:
            result = self.client.list(resources, path, retrieve_all=False)
            next(result)
            self.assertEqual([REQUEST_ID], result.request_ids)
            next(result)
            self.assertEqual([REQUEST_ID, REQUEST_ID], result.request_ids)

        self.assertEqual(2, mock_request.call_count)
        mock_request.assert_has_calls([
            mock.call(
                end_url(path, ""), 'GET',
                body=None,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN})),
            mock.call(
                MyUrlComparator(end_url(path, fake_query), self.client), 'GET',
                body=None,
                headers=ContainsKeyValue({'X-Auth-Token': TOKEN}))])

    def test_deserialize_without_data(self):
        data = u''
        result = self.client.deserialize(data, 200)
        self.assertEqual(data, result)

    def test_update_resource(self):
        params = {'test': 'value'}
        expect_query = six.moves.urllib.parse.urlencode(params)
        self.client.httpclient.auth_token = 'token'
        body = params
        expect_body = self.client.serialize(body)
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = (MyResp(200, resp_headers), expect_body)

        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            result = self.client._update_resource('/test', body=body,
                                                  params=params)

        mock_request.assert_called_once_with(
            MyUrlComparator(end_url('/test', query=expect_query), self.client),
            'PUT', body=expect_body,
            headers=ContainsKeyValue({'X-Auth-Token': 'token'}))
        self.assertNotIn('If-Match', mock_request.call_args[1]['headers'])

        self.assertEqual(body, result)
        self.assertEqual([REQUEST_ID], result.request_ids)

    def test_update_resource_with_revision_number(self):
        params = {'test': 'value'}
        expect_query = six.moves.urllib.parse.urlencode(params)
        self.client.httpclient.auth_token = 'token'
        body = params
        expect_body = self.client.serialize(body)
        resp_headers = {'x-openstack-request-id': REQUEST_ID}
        resp = (MyResp(200, resp_headers), expect_body)

        with mock.patch.object(self.client.httpclient, "request",
                               return_value=resp) as mock_request:
            result = self.client._update_resource('/test', body=body,
                                                  params=params,
                                                  revision_number=1)

        mock_request.assert_called_once_with(
            MyUrlComparator(end_url('/test', query=expect_query), self.client),
            'PUT', body=expect_body,
            headers=ContainsKeyValue(
                {'X-Auth-Token': 'token', 'If-Match': 'revision_number=1'}))

        self.assertEqual(body, result)
        self.assertEqual([REQUEST_ID], result.request_ids)


class CLITestV20ExceptionHandler(CLITestV20Base):

    def _test_exception_handler_v20(
            self, expected_exception, status_code, expected_msg,
            error_type=None, error_msg=None, error_detail=None,
            request_id=None, error_content=None):

        resp = MyResp(status_code, {'x-openstack-request-id': request_id})
        if request_id is not None:
            expected_msg += "\nNeutron server returns " \
                            "request_ids: %s" % [request_id]
        if error_content is None:
            error_content = {'NeutronError': {'type': error_type,
                                              'message': error_msg,
                                              'detail': error_detail}}
        expected_content = self.client._convert_into_with_meta(error_content,
                                                               resp)

        e = self.assertRaises(expected_exception,
                              client.exception_handler_v20,
                              status_code, expected_content)
        self.assertEqual(status_code, e.status_code)
        self.assertEqual(expected_exception.__name__,
                         e.__class__.__name__)

        if expected_msg is None:
            if error_detail:
                expected_msg = '\n'.join([error_msg, error_detail])
            else:
                expected_msg = error_msg
        self.assertEqual(expected_msg, e.message)

    def test_exception_handler_v20_ip_address_in_use(self):
        err_msg = ('Unable to complete operation for network '
                   'fake-network-uuid. The IP address fake-ip is in use.')
        self._test_exception_handler_v20(
            exceptions.IpAddressInUseClient, 409, err_msg,
            'IpAddressInUse', err_msg, '', REQUEST_ID)

    def test_exception_handler_v20_neutron_known_error(self):
        known_error_map = [
            ('NetworkNotFound', exceptions.NetworkNotFoundClient, 404),
            ('PortNotFound', exceptions.PortNotFoundClient, 404),
            ('NetworkInUse', exceptions.NetworkInUseClient, 409),
            ('PortInUse', exceptions.PortInUseClient, 409),
            ('StateInvalid', exceptions.StateInvalidClient, 400),
            ('IpAddressInUse', exceptions.IpAddressInUseClient, 409),
            ('IpAddressGenerationFailure',
             exceptions.IpAddressGenerationFailureClient, 409),
            ('MacAddressInUse', exceptions.MacAddressInUseClient, 409),
            ('ExternalIpAddressExhausted',
             exceptions.ExternalIpAddressExhaustedClient, 400),
            ('OverQuota', exceptions.OverQuotaClient, 409),
            ('InvalidIpForNetwork', exceptions.InvalidIpForNetworkClient, 400),
            ('InvalidIpForSubnet', exceptions.InvalidIpForSubnetClient, 400),
            ('IpAddressAlreadyAllocated',
             exceptions.IpAddressAlreadyAllocatedClient, 400),
        ]

        error_msg = 'dummy exception message'
        error_detail = 'sample detail'
        for server_exc, client_exc, status_code in known_error_map:
            self._test_exception_handler_v20(
                client_exc, status_code,
                error_msg + '\n' + error_detail,
                server_exc, error_msg, error_detail, REQUEST_ID)

    def test_exception_handler_v20_neutron_known_error_without_detail(self):
        error_msg = 'Network not found'
        error_detail = ''
        self._test_exception_handler_v20(
            exceptions.NetworkNotFoundClient, 404,
            error_msg,
            'NetworkNotFound', error_msg, error_detail, REQUEST_ID)

    def test_exception_handler_v20_unknown_error_to_per_code_exception(self):
        for status_code, client_exc in exceptions.HTTP_EXCEPTION_MAP.items():
            error_msg = 'Unknown error'
            error_detail = 'This is detail'
            self._test_exception_handler_v20(
                client_exc, status_code,
                error_msg + '\n' + error_detail,
                'UnknownError', error_msg, error_detail, [REQUEST_ID])

    def test_exception_handler_v20_neutron_unknown_status_code(self):
        error_msg = 'Unknown error'
        error_detail = 'This is detail'
        self._test_exception_handler_v20(
            exceptions.NeutronClientException, 501,
            error_msg + '\n' + error_detail,
            'UnknownError', error_msg, error_detail, REQUEST_ID)

    def test_exception_handler_v20_bad_neutron_error(self):
        for status_code, client_exc in exceptions.HTTP_EXCEPTION_MAP.items():
            error_content = {'NeutronError': {'unknown_key': 'UNKNOWN'}}
            self._test_exception_handler_v20(
                client_exc, status_code,
                expected_msg="{'unknown_key': 'UNKNOWN'}",
                error_content=error_content,
                request_id=REQUEST_ID)

    def test_exception_handler_v20_error_dict_contains_message(self):
        error_content = {'message': 'This is an error message'}
        for status_code, client_exc in exceptions.HTTP_EXCEPTION_MAP.items():
            self._test_exception_handler_v20(
                client_exc, status_code,
                expected_msg='This is an error message',
                error_content=error_content,
                request_id=REQUEST_ID)

    def test_exception_handler_v20_error_dict_not_contain_message(self):
        # 599 is not contained in HTTP_EXCEPTION_MAP.
        error_content = {'error': 'This is an error message'}
        expected_msg = '%s-%s' % (599, error_content)
        self._test_exception_handler_v20(
            exceptions.NeutronClientException, 599,
            expected_msg=expected_msg,
            request_id=None,
            error_content=error_content)

    def test_exception_handler_v20_default_fallback(self):
        # 599 is not contained in HTTP_EXCEPTION_MAP.
        error_content = 'This is an error message'
        expected_msg = '%s-%s' % (599, error_content)
        self._test_exception_handler_v20(
            exceptions.NeutronClientException, 599,
            expected_msg=expected_msg,
            request_id=None,
            error_content=error_content)

    def test_exception_status(self):
        e = exceptions.BadRequest()
        self.assertEqual(400, e.status_code)

        e = exceptions.BadRequest(status_code=499)
        self.assertEqual(499, e.status_code)

        # SslCertificateValidationError has no explicit status_code,
        # but should have a 'safe' defined fallback.
        e = exceptions.SslCertificateValidationError()
        self.assertIsNotNone(e.status_code)

        e = exceptions.SslCertificateValidationError(status_code=599)
        self.assertEqual(599, e.status_code)

    def test_connection_failed(self):
        self.client.httpclient.auth_token = 'token'
        excp = requests.exceptions.ConnectionError('Connection refused')

        with mock.patch.object(self.client.httpclient, "request",
                               side_effect=excp) as mock_request:
            error = self.assertRaises(exceptions.ConnectionFailed,
                                      self.client.get, '/test')

        mock_request.assert_called_once_with(
            end_url('/test'), 'GET',
            body=None,
            headers=ContainsKeyValue({'X-Auth-Token': 'token'}))
        # NB: ConnectionFailed has no explicit status_code, so this
        # tests that there is a fallback defined.
        self.assertIsNotNone(error.status_code)


class DictWithMetaTest(base.BaseTestCase):

    def test_dict_with_meta(self):
        body = {'test': 'value'}
        resp = MyResp(200, {'x-openstack-request-id': REQUEST_ID})
        obj = client._DictWithMeta(body, resp)
        self.assertEqual(body, obj)

        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)


class TupleWithMetaTest(base.BaseTestCase):

    def test_tuple_with_meta(self):
        body = ('test', 'value')
        resp = MyResp(200, {'x-openstack-request-id': REQUEST_ID})
        obj = client._TupleWithMeta(body, resp)
        self.assertEqual(body, obj)

        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)


class StrWithMetaTest(base.BaseTestCase):

    def test_str_with_meta(self):
        body = "test_string"
        resp = MyResp(200, {'x-openstack-request-id': REQUEST_ID})
        obj = client._StrWithMeta(body, resp)
        self.assertEqual(body, obj)

        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)


class GeneratorWithMetaTest(base.BaseTestCase):

    body = {'test': 'value'}
    resp = MyResp(200, {'x-openstack-request-id': REQUEST_ID})

    def _pagination(self, collection, path, **params):
        obj = client._DictWithMeta(self.body, self.resp)
        yield obj

    def test_generator(self):
        obj = client._GeneratorWithMeta(self._pagination, 'test_collection',
                                        'test_path', test_args='test_args')
        self.assertEqual(self.body, next(obj))

        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual([REQUEST_ID], obj.request_ids)


class CLITestV20OutputFormatter(CLITestV20Base):

    def _test_create_resource_with_formatter(self, fmt):
        resource = 'network'
        cmd = network.CreateNetwork(MyApp(sys.stdout), None)
        args = ['-f', fmt, 'myname']
        position_names = ['name']
        position_values = ['myname']
        self._test_create_resource(resource, cmd, 'myname', 'myid', args,
                                   position_names, position_values)

    def test_create_resource_table(self):
        self._test_create_resource_with_formatter('table')
        print(self.fake_stdout.content)
        # table data is contains in the third element.
        data = self.fake_stdout.content[2].split('\n')
        self.assertTrue(any(' id ' in d for d in data))
        self.assertTrue(any(' name ' in d for d in data))

    def test_create_resource_json(self):
        self._test_create_resource_with_formatter('json')
        data = jsonutils.loads(self.fake_stdout.make_string())
        self.assertEqual('myname', data['name'])
        self.assertEqual('myid', data['id'])

    def test_create_resource_yaml(self):
        self._test_create_resource_with_formatter('yaml')
        data = yaml.load(self.fake_stdout.make_string())
        self.assertEqual('myname', data['name'])
        self.assertEqual('myid', data['id'])

    def _test_show_resource_with_formatter(self, fmt):
        resource = 'network'
        cmd = network.ShowNetwork(MyApp(sys.stdout), None)
        args = ['-f', fmt, '-F', 'id', '-F', 'name', 'myid']
        self._test_show_resource(resource, cmd, 'myid',
                                 args, ['id', 'name'])

    def test_show_resource_table(self):
        self._test_show_resource_with_formatter('table')
        data = self.fake_stdout.content[0].split('\n')
        self.assertTrue(any(' id ' in d for d in data))
        self.assertTrue(any(' name ' in d for d in data))

    def test_show_resource_json(self):
        self._test_show_resource_with_formatter('json')
        data = jsonutils.loads(''.join(self.fake_stdout.content))
        self.assertEqual('myname', data['name'])
        self.assertEqual('myid', data['id'])

    def test_show_resource_yaml(self):
        self._test_show_resource_with_formatter('yaml')
        data = yaml.load(''.join(self.fake_stdout.content))
        self.assertEqual('myname', data['name'])
        self.assertEqual('myid', data['id'])

    @mock.patch.object(network.ListNetwork, "extend_list")
    def _test_list_resources_with_formatter(self, fmt, mock_extend_list):
        resources = 'networks'
        cmd = network.ListNetwork(MyApp(sys.stdout), None)
        # ListNetwork has its own extend_list, so we need to stub out it
        # to avoid an extra API call.
        self._test_list_resources(resources, cmd, output_format=fmt)
        mock_extend_list.assert_called_once_with(IsA(list), mock.ANY)

    def test_list_resources_table(self):
        self._test_list_resources_with_formatter('table')
        data = self.fake_stdout.content[0].split('\n')
        self.assertTrue(any(' id ' in d for d in data))
        self.assertTrue(any(' myid1 ' in d for d in data))
        self.assertTrue(any(' myid2 ' in d for d in data))

    def test_list_resources_json(self):
        self._test_list_resources_with_formatter('json')
        data = jsonutils.loads(''.join(self.fake_stdout.content))
        self.assertEqual(['myid1', 'myid2'], [d['id'] for d in data])

    def test_list_resources_yaml(self):
        self._test_list_resources_with_formatter('yaml')
        data = yaml.load(''.join(self.fake_stdout.content))
        self.assertEqual(['myid1', 'myid2'], [d['id'] for d in data])
