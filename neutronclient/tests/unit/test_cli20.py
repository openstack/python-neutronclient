# Copyright 2012 OpenStack LLC.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import urllib

import fixtures
import mox
import testtools

from neutronclient.common import constants
from neutronclient.neutron import v2_0 as neutronV2_0
from neutronclient import shell
from neutronclient.v2_0 import client

API_VERSION = "2.0"
FORMAT = 'json'
TOKEN = 'testtoken'
ENDURL = 'localurl'


class FakeStdout:

    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result = result + line
        return result


class MyResp(object):
    def __init__(self, status):
        self.status = status


class MyApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout


def end_url(path, query=None, format=FORMAT):
    _url_str = ENDURL + "/v" + API_VERSION + path + "." + format
    return query and _url_str + "?" + query or _url_str


class MyUrlComparator(mox.Comparator):
    def __init__(self, lhs, client):
        self.lhs = lhs
        self.client = client

    def equals(self, rhs):
        return str(self) == rhs

    def __str__(self):
        if self.client and self.client.format != FORMAT:
            lhs_parts = self.lhs.split("?", 1)
            if len(lhs_parts) == 2:
                lhs = ("%s.%s?%s" % (lhs_parts[0][:-4],
                                     self.client.format,
                                     lhs_parts[1]))
            else:
                lhs = ("%s.%s" % (lhs_parts[0][:-4],
                                  self.client.format))
            return lhs
        return self.lhs

    def __repr__(self):
        return str(self)


class MyComparator(mox.Comparator):
    def __init__(self, lhs, client):
        self.lhs = lhs
        self.client = client

    def _com_dict(self, lhs, rhs):
        if len(lhs) != len(rhs):
            return False
        for key, value in lhs.iteritems():
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

    def equals(self, rhs):
        if self.client:
            rhs = self.client.deserialize(rhs, 200)
        return self._com(self.lhs, rhs)

    def __repr__(self):
        if self.client:
            return self.client.serialize(self.lhs)
        return str(self.lhs)


class CLITestV20Base(testtools.TestCase):

    format = 'json'
    test_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    id_field = 'id'

    def _find_resourceid(self, client, resource, name_or_id):
        return name_or_id

    def _get_attr_metadata(self):
        return self.metadata
        client.Client.EXTED_PLURALS.update(constants.PLURALS)
        client.Client.EXTED_PLURALS.update({'tags': 'tag'})
        return {'plurals': client.Client.EXTED_PLURALS,
                'xmlns': constants.XML_NS_V20,
                constants.EXT_NS: {'prefix': 'http://xxxx.yy.com'}}

    def setUp(self, plurals={}):
        """Prepare the test environment."""
        super(CLITestV20Base, self).setUp()
        client.Client.EXTED_PLURALS.update(constants.PLURALS)
        client.Client.EXTED_PLURALS.update(plurals)
        self.metadata = {'plurals': client.Client.EXTED_PLURALS,
                         'xmlns': constants.XML_NS_V20,
                         constants.EXT_NS: {'prefix':
                                            'http://xxxx.yy.com'}}
        self.mox = mox.Mox()
        self.endurl = ENDURL
        self.fake_stdout = FakeStdout()
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.fake_stdout))
        self.useFixture(fixtures.MonkeyPatch(
            'neutronclient.neutron.v2_0.find_resourceid_by_name_or_id',
            self._find_resourceid))
        self.useFixture(fixtures.MonkeyPatch(
            'neutronclient.v2_0.client.Client.get_attr_metadata',
            self._get_attr_metadata))
        self.client = client.Client(token=TOKEN, endpoint_url=self.endurl)

    def _test_create_resource(self, resource, cmd,
                              name, myid, args,
                              position_names, position_values, tenant_id=None,
                              tags=None, admin_state_up=True, shared=False,
                              extra_body=None, **kwargs):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        non_admin_status_resources = ['subnet', 'floatingip', 'security_group',
                                      'security_group_rule', 'qos_queue',
                                      'network_gateway', 'credential',
                                      'network_profile', 'policy_profile',
                                      'ikepolicy', 'ipsecpolicy']
        if (resource in non_admin_status_resources):
            body = {resource: {}, }
        else:
            body = {resource: {'admin_state_up': admin_state_up, }, }
        if tenant_id:
            body[resource].update({'tenant_id': tenant_id})
        if tags:
            body[resource].update({'tags': tags})
        if shared:
            body[resource].update({'shared': shared})
        if extra_body:
            body[resource].update(extra_body)
        body[resource].update(kwargs)

        for i in xrange(len(position_names)):
            body[resource].update({position_names[i]: position_values[i]})
        ress = {resource:
                {self.id_field: myid}, }
        if name:
            ress[resource].update({'name': name})
        self.client.format = self.format
        resstr = self.client.serialize(ress)
        # url method body
        resource_plural = neutronV2_0._get_resource_plural(resource,
                                                           self.client)
        path = getattr(self.client, resource_plural + "_path")
        # Work around for LP #1217791. XML deserializer called from
        # MyComparator does not decodes XML string correctly.
        if self.format == 'json':
            mox_body = MyComparator(body, self.client)
        else:
            mox_body = self.client.serialize(body)
        self.client.httpclient.request(
            end_url(path, format=self.format), 'POST',
            body=mox_body,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser('create_' + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)
        if name:
            self.assertTrue(name in _str)

    def _test_list_columns(self, cmd, resources_collection,
                           resources_out, args=['-f', 'json']):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        self.client.format = self.format
        resstr = self.client.serialize(resources_out)

        path = getattr(self.client, resources_collection + "_path")
        self.client.httpclient.request(
            end_url(path, format=self.format), 'GET',
            body=None,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources_collection)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def _test_list_resources(self, resources, cmd, detail=False, tags=[],
                             fields_1=[], fields_2=[], page_size=None,
                             sort_key=[], sort_dir=[], response_contents=None,
                             base_args=None, path=None):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        if response_contents is None:
            contents = [{self.id_field: 'myid1', },
                        {self.id_field: 'myid2', }, ]
        else:
            contents = response_contents
        reses = {resources: contents}
        self.client.format = self.format
        resstr = self.client.serialize(reses)
        # url method body
        query = ""
        args = base_args if base_args is not None else []
        if detail:
            args.append('-D')
        args.extend(['--request-format', self.format])
        if fields_1:
            for field in fields_1:
                args.append('--fields')
                args.append(field)

        if tags:
            args.append('--')
            args.append("--tag")
        for tag in tags:
            args.append(tag)
            if isinstance(tag, unicode):
                tag = urllib.quote(tag.encode('utf-8'))
            if query:
                query += "&tag=" + tag
            else:
                query = "tag=" + tag
        if (not tags) and fields_2:
            args.append('--')
        if fields_2:
            args.append("--fields")
            for field in fields_2:
                args.append(field)
        if detail:
            query = query and query + '&verbose=True' or 'verbose=True'
        fields_1.extend(fields_2)
        for field in fields_1:
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
                sort_dir += ['asc'] * len_diff
            elif len_diff < 0:
                sort_dir = sort_dir[:len(sort_key)]
            for dir in sort_dir:
                args.append('--sort-dir')
                args.append(dir)
                if query:
                    query += '&'
                query += 'sort_dir=%s' % dir
        if path is None:
            path = getattr(self.client, resources + "_path")
        self.client.httpclient.request(
            MyUrlComparator(end_url(path, query, format=self.format),
                            self.client),
            'GET',
            body=None,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        if response_contents is None:
            self.assertTrue('myid1' in _str)
        return _str

    def _test_list_resources_with_pagination(self, resources, cmd):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        path = getattr(self.client, resources + "_path")
        fake_query = "marker=myid2&limit=2"
        reses1 = {resources: [{'id': 'myid1', },
                              {'id': 'myid2', }],
                  '%s_links' % resources: [{'href': end_url(path, fake_query),
                                            'rel': 'next'}]}
        reses2 = {resources: [{'id': 'myid3', },
                              {'id': 'myid4', }]}
        self.client.format = self.format
        resstr1 = self.client.serialize(reses1)
        resstr2 = self.client.serialize(reses2)
        self.client.httpclient.request(
            end_url(path, "", format=self.format), 'GET',
            body=None,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr1))
        self.client.httpclient.request(
            end_url(path, fake_query, format=self.format), 'GET',
            body=None,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr2))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        args = ['--request-format', self.format]
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def _test_update_resource(self, resource, cmd, myid, args, extrafields):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        body = {resource: extrafields}
        path = getattr(self.client, resource + "_path")
        self.client.format = self.format
        # Work around for LP #1217791. XML deserializer called from
        # MyComparator does not decodes XML string correctly.
        if self.format == 'json':
            mox_body = MyComparator(body, self.client)
        else:
            mox_body = self.client.serialize(body)
        self.client.httpclient.request(
            MyUrlComparator(end_url(path % myid, format=self.format),
                            self.client),
            'PUT',
            body=mox_body,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(204), None))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("update_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)

    def _test_show_resource(self, resource, cmd, myid, args, fields=[]):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        query = "&".join(["fields=%s" % field for field in fields])
        expected_res = {resource:
                        {self.id_field: myid,
                         'name': 'myname', }, }
        self.client.format = self.format
        resstr = self.client.serialize(expected_res)
        path = getattr(self.client, resource + "_path")
        self.client.httpclient.request(
            end_url(path % myid, query, format=self.format), 'GET',
            body=None,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("show_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)
        self.assertTrue('myname' in _str)

    def _test_delete_resource(self, resource, cmd, myid, args):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        path = getattr(self.client, resource + "_path")
        self.client.httpclient.request(
            end_url(path % myid, format=self.format), 'DELETE',
            body=None,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(204), None))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("delete_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)

    def _test_update_resource_action(self, resource, cmd, myid, action, args,
                                     body, retval=None):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        path = getattr(self.client, resource + "_path")
        path_action = '%s/%s' % (myid, action)
        self.client.httpclient.request(
            end_url(path % path_action, format=self.format), 'PUT',
            body=MyComparator(body, self.client),
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(204), retval))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("delete_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)


class ClientV2UnicodeTestJson(CLITestV20Base):
    def test_do_request(self):
        self.client.format = self.format
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        unicode_text = u'\u7f51\u7edc'
        # url with unicode
        action = u'/test'
        expected_action = action.encode('utf-8')
        # query string with unicode
        params = {'test': unicode_text}
        expect_query = urllib.urlencode({'test':
                                         unicode_text.encode('utf-8')})
        # request body with unicode
        body = params
        expect_body = self.client.serialize(body)
        # headers with unicode
        self.client.httpclient.auth_token = unicode_text
        expected_auth_token = unicode_text.encode('utf-8')

        self.client.httpclient.request(
            end_url(expected_action, query=expect_query, format=self.format),
            'PUT', body=expect_body,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token',
                expected_auth_token)).AndReturn((MyResp(200), expect_body))

        self.mox.ReplayAll()
        res_body = self.client.do_request('PUT', action, body=body,
                                          params=params)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

        # test response with unicode
        self.assertEqual(res_body, body)


class ClientV2UnicodeTestXML(ClientV2UnicodeTestJson):
    format = 'xml'
