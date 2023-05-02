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
from unittest import mock

from neutronclient.osc.v2.dynamic_routing import bgp_speaker
from neutronclient.tests.unit.osc.v2.dynamic_routing import fakes


class TestListBgpSpeaker(fakes.TestNeutronDynamicRoutingOSCV2):
    _bgp_speakers = fakes.FakeBgpSpeaker.create_bgp_speakers()
    columns = ('ID', 'Name', 'Local AS', 'IP Version')
    data = []
    for _bgp_speaker in _bgp_speakers:
        data.append((
            _bgp_speaker['id'],
            _bgp_speaker['name'],
            _bgp_speaker['local_as'],
            _bgp_speaker['ip_version']))

    def setUp(self):
        super(TestListBgpSpeaker, self).setUp()

        self.networkclient.bgp_speakers = mock.Mock(
            return_value=self._bgp_speakers
        )

        # Get the command object to test
        self.cmd = bgp_speaker.ListBgpSpeaker(self.app, self.namespace)

    def test_bgp_speaker_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)
        self.networkclient.bgp_speakers.assert_called_once_with(
            retrieve_all=True)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestDeleteBgpSpeaker(fakes.TestNeutronDynamicRoutingOSCV2):

    _bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()

    def setUp(self):
        super(TestDeleteBgpSpeaker, self).setUp()

        self.networkclient.delete_bgp_speaker = mock.Mock(return_value=None)

        self.cmd = bgp_speaker.DeleteBgpSpeaker(self.app, self.namespace)

    def test_delete_bgp_speaker(self):
        arglist = [
            self._bgp_speaker['name'],
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.networkclient.delete_bgp_speaker.assert_called_once_with(
            self._bgp_speaker['name'])
        self.assertIsNone(result)


class TestShowBgpSpeaker(fakes.TestNeutronDynamicRoutingOSCV2):
    _one_bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    data = (
        _one_bgp_speaker['advertise_floating_ip_host_routes'],
        _one_bgp_speaker['advertise_tenant_networks'],
        _one_bgp_speaker['id'],
        _one_bgp_speaker['ip_version'],
        _one_bgp_speaker['local_as'],
        _one_bgp_speaker['name'],
        _one_bgp_speaker['networks'],
        _one_bgp_speaker['peers'],
        _one_bgp_speaker['tenant_id']
    )
    _bgp_speaker = _one_bgp_speaker
    _bgp_speaker_name = _one_bgp_speaker['name']
    columns = (
        'advertise_floating_ip_host_routes',
        'advertise_tenant_networks',
        'id',
        'ip_version',
        'local_as',
        'name',
        'networks',
        'peers',
        'project_id'
    )

    def setUp(self):
        super(TestShowBgpSpeaker, self).setUp()

        self.networkclient.get_bgp_speaker = mock.Mock(
            return_value=self._bgp_speaker
        )
        # Get the command object to test
        self.cmd = bgp_speaker.ShowBgpSpeaker(self.app, self.namespace)

    def test_bgp_speaker_show(self):
        arglist = [
            self._bgp_speaker_name,
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        data = self.cmd.take_action(parsed_args)
        self.networkclient.get_bgp_speaker.assert_called_once_with(
            self._bgp_speaker_name)
        self.assertEqual(self.columns, data[0])
        self.assertEqual(self.data, data[1])


class TestSetBgpSpeaker(fakes.TestNeutronDynamicRoutingOSCV2):
    _one_bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    _bgp_speaker_name = _one_bgp_speaker['name']

    def setUp(self):
        super(TestSetBgpSpeaker, self).setUp()
        self.networkclient.update_bgp_speaker = mock.Mock(
            return_value=None)

        self.cmd = bgp_speaker.SetBgpSpeaker(self.app, self.namespace)

    def test_set_bgp_speaker(self):
        arglist = [
            self._bgp_speaker_name,
            '--name', 'noob',
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_name),
            ('name', 'noob'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'name': 'noob'}
        self.networkclient.update_bgp_speaker.assert_called_once_with(
            self._bgp_speaker_name, **attrs)
        self.assertIsNone(result)
