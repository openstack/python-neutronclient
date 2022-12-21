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

from neutronclient.osc.v2.dynamic_routing import bgp_peer
from neutronclient.tests.unit.osc.v2.dynamic_routing import fakes


class TestListBgpPeer(fakes.TestNeutronDynamicRoutingOSCV2):
    _bgp_peers = fakes.FakeBgpPeer.create_bgp_peers(count=1)
    columns = ('ID', 'Name', 'Peer IP', 'Remote AS')
    data = []
    for _bgp_peer in _bgp_peers:
        data.append((
            _bgp_peer['id'],
            _bgp_peer['name'],
            _bgp_peer['peer_ip'],
            _bgp_peer['remote_as']))

    def setUp(self):
        super(TestListBgpPeer, self).setUp()

        self.networkclient.bgp_peers = mock.Mock(
            return_value=self._bgp_peers
        )

        # Get the command object to test
        self.cmd = bgp_peer.ListBgpPeer(self.app, self.namespace)

    def test_bgp_peer_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)
        self.networkclient.bgp_peers.assert_called_once_with(
            retrieve_all=True)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestDeleteBgpPeer(fakes.TestNeutronDynamicRoutingOSCV2):

    _bgp_peer = fakes.FakeBgpPeer.create_one_bgp_peer()

    def setUp(self):
        super(TestDeleteBgpPeer, self).setUp()

        self.networkclient.delete_bgp_peer = mock.Mock(return_value=None)

        self.cmd = bgp_peer.DeleteBgpPeer(self.app, self.namespace)

    def test_delete_bgp_peer(self):
        arglist = [
            self._bgp_peer['name'],
        ]
        verifylist = [
            ('bgp_peer', self._bgp_peer['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.networkclient.delete_bgp_peer.assert_called_once_with(
            self._bgp_peer['name'])
        self.assertIsNone(result)


class TestShowBgpPeer(fakes.TestNeutronDynamicRoutingOSCV2):
    _one_bgp_peer = fakes.FakeBgpPeer.create_one_bgp_peer()
    data = (
        _one_bgp_peer['auth_type'],
        _one_bgp_peer['id'],
        _one_bgp_peer['name'],
        _one_bgp_peer['peer_ip'],
        _one_bgp_peer['tenant_id'],
        _one_bgp_peer['remote_as'],
    )
    _bgp_peer = _one_bgp_peer
    _bgp_peer_name = _one_bgp_peer['name']
    columns = (
        'auth_type',
        'id',
        'name',
        'peer_ip',
        'project_id',
        'remote_as',
    )

    def setUp(self):
        super(TestShowBgpPeer, self).setUp()

        self.networkclient.get_bgp_peer = mock.Mock(
            return_value=self._bgp_peer
        )
        # Get the command object to test
        self.cmd = bgp_peer.ShowBgpPeer(self.app, self.namespace)

    def test_bgp_peer_show(self):
        arglist = [
            self._bgp_peer_name,
        ]
        verifylist = [
            ('bgp_peer', self._bgp_peer_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        data = self.cmd.take_action(parsed_args)
        self.networkclient.get_bgp_peer.assert_called_once_with(
            self._bgp_peer_name)
        self.assertEqual(self.columns, data[0])
        self.assertEqual(self.data, data[1])


class TestSetBgpPeer(fakes.TestNeutronDynamicRoutingOSCV2):
    _one_bgp_peer = fakes.FakeBgpPeer.create_one_bgp_peer()
    _bgp_peer_name = _one_bgp_peer['name']

    def setUp(self):
        super(TestSetBgpPeer, self).setUp()
        self.networkclient.update_bgp_peer = mock.Mock(return_value=None)
        bgp_peer.get_bgp_peer_id = mock.Mock(return_value=self._bgp_peer_name)

        self.cmd = bgp_peer.SetBgpPeer(self.app, self.namespace)

    def test_set_bgp_peer(self):
        arglist = [
            self._bgp_peer_name,
            '--name', 'noob',
        ]
        verifylist = [
            ('bgp_peer', self._bgp_peer_name),
            ('name', 'noob'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'name': 'noob', 'password': None}
        self.networkclient.update_bgp_peer.assert_called_once_with(
            self._bgp_peer_name, **attrs)
        self.assertIsNone(result)
