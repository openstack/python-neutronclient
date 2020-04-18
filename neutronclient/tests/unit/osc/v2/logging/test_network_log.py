# Copyright 2017-2018 FUJITSU LIMITED
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

import copy
from unittest import mock

from osc_lib import exceptions
from osc_lib.tests import utils
import testtools

from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.logging import network_log
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes
from neutronclient.tests.unit.osc.v2.logging import fakes


_log = fakes.NetworkLog().create()
RES_TYPE_SG = 'security_group'
RES_TYPE_FWG = 'firewall_group'
CONVERT_MAP = {
    'project': 'project_id',
    'enable': 'enabled',
    'disable': 'enabled',
    'target': 'target_id',
    'resource': 'resource_id',
    'event': 'event',
}


def _generate_data(ordered_dict=None, data=None):
    source = ordered_dict if ordered_dict else _log
    if data:
        source.update(data)
    return tuple(source[key] for key in source)


def _generate_req_and_res(verifylist):
    request = dict(verifylist)
    response = copy.deepcopy(_log)
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        if key == 'enable' and val:
            new_value = True
        elif key == 'disable' and val:
            new_value = False
        else:
            new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestNetworkLog(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {'logs': [exp_req]}
        else:
            req_body = {'log': exp_req}
        self.mocked.assert_called_once_with(req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super(TestNetworkLog, self).setUp()
        self.neutronclient.find_resource = mock.Mock()
        self.neutronclient.find_resource.side_effect = \
            lambda x, y, **k: {'id': y}
        osc_utils.find_project = mock.Mock()
        osc_utils.find_project.id = _log['project_id']
        self.res = _log
        self.headers = (
            'ID',
            'Description',
            'Enabled',
            'Name',
            'Target',
            'Project',
            'Resource',
            'Type',
            'Event',
        )
        self.data = _generate_data()
        self.ordered_headers = (
            'Description',
            'Enabled',
            'Event',
            'ID',
            'Name',
            'Project',
            'Resource',
            'Target',
            'Type',
        )
        self.ordered_data = (
            _log['description'],
            _log['enabled'],
            _log['event'],
            _log['id'],
            _log['name'],
            _log['project_id'],
            _log['resource_id'],
            _log['target_id'],
            _log['resource_type'],
        )
        self.ordered_columns = (
            'description',
            'enabled',
            'event',
            'id',
            'name',
            'project_id',
            'resource_id',
            'target_id',
            'resource_type',
        )


class TestCreateNetworkLog(TestNetworkLog):

    def setUp(self):
        super(TestCreateNetworkLog, self).setUp()
        self.neutronclient.create_network_log = mock.Mock(
            return_value={'log': _log})
        self.mocked = self.neutronclient.create_network_log
        self.cmd = network_log.CreateNetworkLog(self.app, self.namespace)
        loggables = {
            "loggable_resources": [{"type": RES_TYPE_SG},
                                   {"type": RES_TYPE_FWG}]
        }
        self.neutronclient.list_network_loggable_resources = mock.Mock(
            return_value=loggables)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.neutronclient.create_network_log.return_value = \
            {'log': dict(response)}
        osc_utils.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = _generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name', 'my-log')
        desc = args.get('description', 'my-description-for-log')
        event = args.get('event', 'ACCEPT')
        resource = args.get('resource', 'id-target-log')
        target = args.get('target', 'id-target-log')
        resource_type = args.get('resource_type', 'security_group')
        project = args.get('project_id', 'id-my-project')

        arglist = [
            name,
            '--description', desc,
            '--enable',
            '--target', target,
            '--resource', resource,
            '--event', event,
            '--project', project,
            '--resource-type', resource_type,
        ]
        verifylist = [
            ('description', desc),
            ('enable', True),
            ('event', event),
            ('name', name),
            ('target', target),
            ('project', project),
            ('resource', target),
            ('resource_type', resource_type),
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self, args={}):
        arglist, verifylist = self._set_all_params(args)
        request, response = _generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_no_options_and_raise(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_mandatory_params(self):
        name = self.res['name']
        arglist = [
            name,
            '--resource-type', RES_TYPE_SG,
        ]
        verifylist = [
            ('name', name),
            ('resource_type', RES_TYPE_SG),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        expect = {
            'name': self.res['name'],
            'resource_type': self.res['resource_type'],
        }
        self.mocked.assert_called_once_with({'log': expect})
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def test_create_with_disable(self):
        name = self.res['name']
        arglist = [
            name,
            '--resource-type', RES_TYPE_SG,
            '--disable',
        ]
        verifylist = [
            ('name', name),
            ('resource_type', RES_TYPE_SG),
            ('disable', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        expect = {
            'name': self.res['name'],
            'resource_type': self.res['resource_type'],
            'enabled': False,
        }
        self.mocked.assert_called_once_with({'log': expect})
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def test_create_with_all_params(self):
        self._test_create_with_all_params()

    def test_create_with_all_params_event_drop(self):
        self._test_create_with_all_params({'event': 'DROP'})

    def test_create_with_all_params_event_all(self):
        self._test_create_with_all_params({'event': 'ALL'})

    def test_create_with_all_params_except_event(self):
        arglist, verifylist = self._set_all_params({'event': ''})
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_all_params_event_upper_capitalized(self):
        for event in ('all', 'All', 'dROP', 'accePt', 'accept', 'drop'):
            arglist, verifylist = self._set_all_params({'event': event})
            self.assertRaises(
                testtools.matchers._impl.MismatchError,
                self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_all_params_resource_type_upper_capitalized(self):
        for res_type in ('SECURITY_GROUP', 'Security_group', 'security_Group'):
            arglist, verifylist = self._set_all_params(
                {'resource_type': res_type})
            self.assertRaises(
                testtools.matchers._impl.MismatchError,
                self.check_parser, self.cmd, arglist, verifylist)

    def test_create_with_valid_fwg_resource(self):
        name = self.res['name']
        resource_id = 'valid_fwg_id'
        resource_type = RES_TYPE_FWG
        # Test with valid FWG ID
        with mock.patch.object(self.neutronclient, 'find_resource',
                               return_value={'id': resource_id}):
            arglist = [name,
                       '--resource-type', resource_type,
                       '--resource', resource_id
                       ]
            verifylist = [
                ('name', name),
                ('resource_type', resource_type),
                ('resource', resource_id)
            ]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            headers, data = self.cmd.take_action(parsed_args)
            expect = {
                'name': self.res['name'],
                'resource_type': RES_TYPE_FWG,
                'resource_id': 'valid_fwg_id',
            }
            self.neutronclient.find_resource.assert_called_with(
                resource_type,
                resource_id,
                cmd_resource='fwaas_firewall_group')
            self.mocked.assert_called_once_with({'log': expect})
            self.assertEqual(self.ordered_headers, headers)
            self.assertEqual(self.ordered_data, data)

    def test_create_with_invalid_fwg_resource(self):
        name = self.res['name']
        resource_id = 'invalid_fwg_id'
        resource_type = RES_TYPE_FWG
        # Test with invalid FWG ID
        with mock.patch.object(self.neutronclient, 'find_resource',
                               side_effect=exceptions.NotFound(code=0)):
            arglist = [name,
                       '--resource-type', resource_type,
                       '--resource', resource_id
                       ]
            verifylist = [
                ('name', name),
                ('resource_type', resource_type),
                ('resource', resource_id)
            ]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.assertRaises(exceptions.NotFound,
                              self.cmd.take_action,
                              parsed_args)
            self.neutronclient.find_resource.assert_called_with(
                resource_type,
                resource_id,
                cmd_resource='fwaas_firewall_group')
            self.mocked.assert_not_called()

    def test_create_with_invalid_resource_type(self):
        name = self.res['name']
        resource_type = 'invalid_resource_type'
        resource_id = 'valid_fwg_id'
        with mock.patch.object(self.neutronclient, 'find_resource',
                               side_effect=exceptions.NotFound(code=0)):
            arglist = [name,
                       '--resource-type', resource_type,
                       '--resource', resource_id
                       ]
            verifylist = [
                ('name', name),
                ('resource_type', resource_type),
                ('resource', resource_id)
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.assertRaises(exceptions.NotFound,
                              self.cmd.take_action,
                              parsed_args)
            self.neutronclient.find_resource.assert_called_with(
                resource_type,
                resource_id,
                cmd_resource=None)
            self.mocked.assert_not_called()


class TestListNetworkLog(TestNetworkLog):

    def _setup_summary(self, expect=None):
        event = 'Event: ' + self.res['event'].upper()
        target = 'Logged: (None specified)'
        if expect:
            if expect.get('event'):
                event = expect['event']
            if expect.get('resource'):
                target = expect['resource']
        summary = ',\n'.join([event, target])
        self.short_data = (
            expect['id'] if expect else self.res['id'],
            expect['enabled'] if expect else self.res['enabled'],
            expect['name'] if expect else self.res['name'],
            expect['resource_type'] if expect else self.res['resource_type'],
            summary
        )

    def setUp(self):
        super(TestListNetworkLog, self).setUp()
        self.cmd = network_log.ListNetworkLog(self.app, self.namespace)

        self.short_header = (
            'ID',
            'Enabled',
            'Name',
            'Type',
            'Summary',
        )
        self._setup_summary()
        self.neutronclient.list_network_logs = mock.Mock(
            return_value={'logs': [self.res]})
        self.mocked = self.neutronclient.list_network_logs

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)
        self.assertEqual([self.data], list(data))

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))

    def test_list_with_target_and_resource(self):
        arglist = []
        verifylist = []
        target_id = 'aaaaaaaa-aaaa-aaaa-aaaaaaaaaaaaaaaaa'
        resource_id = 'bbbbbbbb-bbbb-bbbb-bbbbbbbbbbbbbbbbb'
        log = fakes.NetworkLog().create({
            'target_id': target_id,
            'resource_id': resource_id})
        self.mocked.return_value = {'logs': [log]}
        logged = 'Logged: (security_group) %(res_id)s on (port) %(t_id)s' % {
            'res_id': resource_id, 't_id': target_id}
        expect_log = copy.deepcopy(log)
        expect_log.update({
            'resource': logged,
            'event': 'Event: ALL'})
        self._setup_summary(expect=expect_log)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))

    def test_list_with_resource(self):
        arglist = []
        verifylist = []
        resource_id = 'bbbbbbbb-bbbb-bbbb-bbbbbbbbbbbbbbbbb'
        log = fakes.NetworkLog().create({'resource_id': resource_id})
        self.mocked.return_value = {'logs': [log]}
        logged = 'Logged: (security_group) %s' % resource_id
        expect_log = copy.deepcopy(log)
        expect_log.update({
            'resource': logged,
            'event': 'Event: ALL'})
        self._setup_summary(expect=expect_log)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))

    def test_list_with_target(self):
        arglist = []
        verifylist = []
        target_id = 'aaaaaaaa-aaaa-aaaa-aaaaaaaaaaaaaaaaa'
        log = fakes.NetworkLog().create({'target_id': target_id})
        self.mocked.return_value = {'logs': [log]}
        logged = 'Logged: (port) %s' % target_id
        expect_log = copy.deepcopy(log)
        expect_log.update({
            'resource': logged,
            'event': 'Event: ALL'})
        self._setup_summary(expect=expect_log)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestShowNetworkLog(TestNetworkLog):

    def setUp(self):
        super(TestShowNetworkLog, self).setUp()
        self.neutronclient.show_network_log = mock.Mock(
            return_value={'log': self.res})
        self.mocked = self.neutronclient.show_network_log
        self.cmd = network_log.ShowNetworkLog(self.app, self.namespace)

    def test_show_filtered_by_id_or_name(self):
        target = self.res['id']
        arglist = [target]
        verifylist = [('network_log', target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)


class TestSetNetworkLog(TestNetworkLog):

    def setUp(self):
        super(TestSetNetworkLog, self).setUp()
        self.neutronclient.update_network_log = mock.Mock(
            return_value={'log': self.res})
        self.mocked = self.neutronclient.update_network_log
        self.cmd = network_log.SetNetworkLog(self.app, self.namespace)

    def test_set_name(self):
        target = self.res['id']
        update = 'change'
        arglist = [target, '--name', update]
        verifylist = [
            ('network_log', target),
            ('name', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {'log': {'name': update}})
        self.assertIsNone(result)

    def test_set_description(self):
        target = self.res['id']
        update = 'change-desc'
        arglist = [target, '--description', update]
        verifylist = [
            ('network_log', target),
            ('description', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {'log': {'description': update}})
        self.assertIsNone(result)

    def test_set_enable(self):
        target = self.res['id']
        arglist = [target, '--enable']
        verifylist = [
            ('network_log', target),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {'log': {'enabled': True}})
        self.assertIsNone(result)

    def test_set_disable(self):
        target = self.res['id']
        arglist = [target, '--disable']
        verifylist = [
            ('network_log', target),
            ('disable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, {'log': {'enabled': False}})
        self.assertIsNone(result)

    # Illegal tests
    def test_illegal_set_resource_type(self):
        target = self.res['id']
        resource_type = 'security_group'
        arglist = [target, '--resource-type', resource_type]
        verifylist = [
            ('network_log', target),
            ('resource_type', resource_type),
        ]

        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_illegal_set_event(self):
        target = self.res['id']
        for event in ['all', 'accept', 'drop']:
            arglist = [target, '--event', event]
            verifylist = [
                ('network_log', target),
                ('event', event),
            ]
            self.assertRaises(
                utils.ParserException,
                self.check_parser, self.cmd, arglist, verifylist)

    def test_illegal_set_resource_id(self):
        target = self.res['id']
        resource_id = 'resource-id-for-logged-target'
        arglist = [target, '--resource', resource_id]
        verifylist = [
            ('network_log', target),
            ('resource', resource_id),
        ]

        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_illegal_set_project(self):
        target = self.res['id']
        arglist = [
            target,
            '--project',
        ]
        verifylist = [
            ('network_log', target),
            ('project', 'other-project'),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_illegal_set_project_domain(self):
        target = self.res['id']
        arglist = [
            target,
            '--project-domain',
        ]
        verifylist = [
            ('network_log', target),
            ('project_domain', 'other-project-domain'),
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)

    def test_illegal_set_and_raises(self):
        self.neutronclient.update_network_log = mock.Mock(
            side_effect=Exception)
        target = self.res['id']
        arglist = [target, '--name', 'my-name']
        verifylist = [('network_log', target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


class TestDeleteNetworkLog(TestNetworkLog):

    def setUp(self):
        super(TestDeleteNetworkLog, self).setUp()
        self.neutronclient.delete_network_log = mock.Mock(
            return_value={'log': self.res})
        self.mocked = self.neutronclient.delete_network_log
        self.cmd = network_log.DeleteNetworkLog(self.app, self.namespace)

    def test_delete_with_one_resource(self):
        target = self.res['id']
        arglist = [target]
        verifylist = [('network_log', [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):
        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [('network_log', [target1, target2])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0])
            self.assertEqual(reference, actual)

    def test_delete_with_no_exist_id(self):
        self.neutronclient.find_resource.side_effect = Exception
        target = 'not_exist'
        arglist = [target]
        verifylist = [('network_log', [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


class TestLoggableResource(test_fakes.TestNeutronClientOSCV2):

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {'logs': [exp_req]}
        else:
            req_body = {'log': exp_req}
        self.mocked.assert_called_once_with(req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super(TestLoggableResource, self).setUp()
        self.headers = ('Supported types',)
        self.data = ('security_group', )


class TestListLoggableResource(TestLoggableResource):

    def setUp(self):
        super(TestListLoggableResource, self).setUp()
        self.cmd = network_log.ListLoggableResource(self.app, self.namespace)

        loggables = {
            "loggable_resources": [{"type": "security_group"}]
        }
        self.neutronclient.list_network_loggable_resources = mock.Mock(
            return_value=loggables)
        self.mocked = self.neutronclient.list_network_loggable_resources

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)
        self.assertEqual([self.data], list(data))

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)
        self.assertEqual([self.data], list(data))
