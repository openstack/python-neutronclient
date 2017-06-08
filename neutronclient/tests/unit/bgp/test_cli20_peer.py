# Copyright 2016 Huawei Technologies India Pvt. Ltd.
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
from neutronclient.neutron.v2_0.bgp import peer as bgp_peer
from neutronclient.neutron.v2_0.bgp import speaker as bgp_speaker
from neutronclient.tests.unit import test_cli20


class CLITestV20BGPPeerJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['bgp_peer']

    def test_create_bgp_peer_with_mandatory_params(self):
        # Create BGP peer with mandatory params.
        resource = 'bgp_peer'
        cmd = bgp_peer.CreatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        name = 'my-name'
        my_id = 'my-id'
        peerip = '1.1.1.1'
        remote_asnum = '1'
        args = [name,
                '--peer-ip', peerip,
                '--remote-as', remote_asnum, ]
        position_names = ['name', 'peer_ip', 'remote_as',
                          'auth_type']
        position_values = [name, peerip, remote_asnum, 'none']
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values)

    def test_create_bgp_peer_with_all_params(self):
        # Create BGP peer with all params.
        resource = 'bgp_peer'
        cmd = bgp_peer.CreatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        name = 'my-name'
        my_id = 'my-id'
        peerip = '1.1.1.1'
        remote_asnum = '65535'
        authType = 'md5'
        password = 'abc'
        args = [name,
                '--peer-ip', peerip,
                '--remote-as', remote_asnum,
                '--auth-type', authType,
                '--password', password]
        position_names = ['name', 'peer_ip', 'remote_as',
                          'auth_type', 'password']
        position_values = [name, peerip, remote_asnum, authType, password]
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values)

    def test_create_bgp_peer_with_invalid_min_remote_asnum(self):
        # Create BGP peer with invalid minimum remote-asnum.
        resource = 'bgp_peer'
        cmd = bgp_peer.CreatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        name = 'my-name'
        my_id = 'my-id'
        peerip = '1.1.1.1'
        remote_asnum = '0'
        args = [name,
                '--peer-ip', peerip,
                '--remote-as', remote_asnum, ]
        position_names = ['name', 'peer_ip', 'remote_as', ]
        position_values = [name, peerip, remote_asnum, ]
        exc = self.assertRaises(exceptions.CommandError,
                                self._test_create_resource,
                                resource, cmd, name, my_id, args,
                                position_names, position_values)
        self.assertEqual('remote-as "0" should be an integer [%s:%s].' %
                         (bgp_speaker.MIN_AS_NUM, bgp_speaker.MAX_AS_NUM),
                         str(exc))

    def test_create_bgp_peer_with_invalid_max_remote_asnum(self):
        # Create BGP peer with invalid maximum remote-asnum.
        resource = 'bgp_peer'
        cmd = bgp_peer.CreatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        name = 'my-name'
        my_id = 'my-id'
        peerip = '1.1.1.1'
        remote_asnum = '65536'
        args = [name,
                '--peer-ip', peerip,
                '--remote-as', remote_asnum, ]
        position_names = ['name', 'peer_ip', 'remote_as',
                          'auth_type', 'password']
        position_values = [name, peerip, remote_asnum, 'none', '']
        exc = self.assertRaises(exceptions.CommandError,
                                self._test_create_resource,
                                resource, cmd, name, my_id, args,
                                position_names, position_values)
        self.assertEqual('remote-as "65536" should be an integer [%s:%s].' %
                         (bgp_speaker.MIN_AS_NUM, bgp_speaker.MAX_AS_NUM),
                         str(exc))

    def test_create_authenticated_bgp_peer_without_authtype(self):
        # Create authenticated BGP peer without auth-type.
        resource = 'bgp_peer'
        cmd = bgp_peer.CreatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        name = 'my-name'
        my_id = 'my-id'
        peerip = '1.1.1.1'
        remote_asnum = '2048'
        password = 'abc'
        args = [name,
                '--peer-ip', peerip,
                '--remote-as', remote_asnum,
                '--password', password]
        position_names = ['name', 'peer_ip', 'remote_as', 'password']
        position_values = [name, peerip, remote_asnum, password]
        exc = self.assertRaises(exceptions.CommandError,
                                self._test_create_resource,
                                resource, cmd, name, my_id, args,
                                position_names, position_values)
        self.assertEqual('Must provide auth-type if password is specified.',
                         str(exc))

    def test_create_authenticated_bgp_peer_without_password(self):
        # Create authenticated BGP peer without password.
        resource = 'bgp_peer'
        cmd = bgp_peer.CreatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        name = 'my-name'
        my_id = 'my-id'
        peerip = '1.1.1.1'
        remote_asnum = '2048'
        authType = 'md5'
        args = [name,
                '--peer-ip', peerip,
                '--remote-as', remote_asnum,
                '--auth-type', authType]
        position_names = ['name', 'peer_ip', 'remote_as', 'auth_type']
        position_values = [name, peerip, remote_asnum, authType]
        exc = self.assertRaises(exceptions.CommandError,
                                self._test_create_resource,
                                resource, cmd, name, my_id, args,
                                position_names, position_values)
        self.assertEqual('Must provide password if auth-type is specified.',
                         str(exc))

    def test_update_bgp_peer(self):
        # Update BGP peer:
        # myid --advertise-tenant-networks True
        #      --advertise-floating-ip-host-routes False
        resource = 'bgp_peer'
        cmd = bgp_peer.UpdatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'new-name',
                                    '--password', 'abc'],
                                   {'name': 'new-name', 'password': 'abc'})

    def test_update_bgp_peer_exception(self):
        # Update BGP peer: myid.
        resource = 'bgp_peer'
        cmd = bgp_peer.UpdatePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        self.assertRaises(exceptions.CommandError,
                          self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_list_bgp_peer(self):
        # List all BGP peers.
        resources = "bgp_peers"
        cmd = bgp_peer.ListPeers(test_cli20.MyApp(sys.stdout),
                                 None)
        self._test_list_resources(resources, cmd, True)

    # TODO(Vikram): Add test_list_bgp_peer_pagination

    def test_list_bgp_peer_sort(self):
        # sorted list: bgp-peer-list --sort-key name --sort-key id
        #                            --sort-key asc --sort-key desc
        resources = "bgp_peers"
        cmd = bgp_peer.ListPeers(test_cli20.MyApp(sys.stdout),
                                 None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_bgp_peer_limit(self):
        # size (1000) limited list: bgp-peer-list -P.
        resources = "bgp_peers"
        cmd = bgp_peer.ListPeers(test_cli20.MyApp(sys.stdout),
                                 None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_show_bgp_peer(self):
        # Show BGP peer: --fields id --fields name myid.
        resource = 'bgp_peer'
        cmd = bgp_peer.ShowPeer(test_cli20.MyApp(sys.stdout),
                                None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_delete_bgp_peer(self):
        # Delete BGP peer: bgp_peer_id.
        resource = 'bgp_peer'
        cmd = bgp_peer.DeletePeer(test_cli20.MyApp(sys.stdout),
                                  None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
