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

import mock

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0.bgp import speaker as bgp_speaker
from neutronclient.tests.unit import test_cli20


class CLITestV20BGPSpeakerJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['bgp_speaker']

    def test_create_bgp_speaker_with_minimal_options(self):
        # Create BGP Speaker with mandatory params.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.CreateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        name = 'my-name'
        my_id = 'my-id'
        local_asnum = '1'
        args = [name, '--local-as', local_asnum, ]
        position_names = ['name', 'local_as', 'ip_version']
        position_values = [name, local_asnum, 4]
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values)

    def test_create_ipv4_bgp_speaker_with_all_params(self):
        # Create BGP Speaker with all params.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.CreateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        name = 'my-name'
        my_id = 'my-id'
        local_asnum = '1'
        args = [name,
                '--local-as', local_asnum,
                '--ip-version', '4',
                '--advertise-floating-ip-host-routes', 'True',
                '--advertise-tenant-networks', 'True']
        position_names = ['name', 'local_as', 'ip_version',
                          'advertise_floating_ip_host_routes',
                          'advertise_tenant_networks']
        position_values = [name, local_asnum, 4, 'True', 'True']
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values)

    def test_create_ipv6_bgp_speaker_with_all_params(self):
        # Create BGP Speaker with all params.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.CreateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        name = 'my-name'
        my_id = 'my-id'
        local_asnum = '65535'
        args = [name,
                '--local-as', local_asnum,
                '--ip-version', '6',
                '--advertise-floating-ip-host-routes', 'True',
                '--advertise-tenant-networks', 'True']
        position_names = ['name', 'local_as', 'ip_version',
                          'advertise_floating_ip_host_routes',
                          'advertise_tenant_networks']
        position_values = [name, local_asnum, 6, 'True', 'True']
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values)

    def test_create_bgp_speaker_with_invalid_min_local_asnum(self):
        # Create BGP Speaker with invalid minimum local-asnum.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.CreateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        name = 'my-name'
        my_id = 'my-id'
        local_asnum = '0'
        args = [name,
                '--local-as', local_asnum]
        position_names = ['name', 'local_as']
        position_values = [name, local_asnum]
        exc = self.assertRaises(exceptions.CommandError,
                                self._test_create_resource,
                                resource, cmd, name, my_id, args,
                                position_names, position_values)
        self.assertEqual('local-as "0" should be an integer [%s:%s].' %
                         (bgp_speaker.MIN_AS_NUM, bgp_speaker.MAX_AS_NUM),
                         str(exc))

    def test_create_bgp_speaker_with_invalid_max_local_asnum(self):
        # Create BGP Speaker with invalid maximum local-asnum.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.CreateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        name = 'my-name'
        my_id = 'my-id'
        local_asnum = '65536'
        args = [name,
                '--local-as', local_asnum]
        position_names = ['name', 'local_as', ]
        position_values = [name, local_asnum, ]
        exc = self.assertRaises(exceptions.CommandError,
                                self._test_create_resource,
                                resource, cmd, name, my_id, args,
                                position_names, position_values)
        self.assertEqual('local-as "65536" should be an integer [%s:%s].' %
                         (bgp_speaker.MIN_AS_NUM, bgp_speaker.MAX_AS_NUM),
                         str(exc))

    def test_update_bgp_speaker(self):
        # Update BGP Speaker:
        # myid --advertise-tenant-networks True
        #      --advertise-floating-ip-host-routes False
        resource = 'bgp_speaker'
        cmd = bgp_speaker.UpdateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid',
                                    '--name', 'new-name',
                                    '--advertise-tenant-networks', 'True',
                                    '--advertise-floating-ip-host-routes',
                                    'False'],
                                   {'name': 'new-name',
                                    'advertise_tenant_networks': 'True',
                                    'advertise_floating_ip_host_routes':
                                    'False'})

    def test_update_bgp_speaker_exception(self):
        # Update BGP Speaker: myid.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.UpdateSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        self.assertRaises(exceptions.CommandError,
                          self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_list_bgp_speaker(self):
        # List all BGP Speakers.
        resources = "bgp_speakers"
        cmd = bgp_speaker.ListSpeakers(test_cli20.MyApp(sys.stdout),
                                       None)
        self._test_list_resources(resources, cmd, True)

    @mock.patch.object(bgp_speaker.ListSpeakers, "extend_list")
    def test_list_bgp_speaker_pagination(self, mock_extend_list):
        # List all BGP Speakers with pagination support.
        cmd = bgp_speaker.ListSpeakers(test_cli20.MyApp(sys.stdout),
                                       None)
        self._test_list_resources_with_pagination("bgp_speakers",
                                                  cmd)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def test_list_bgp_speaker_sort(self):
        # sorted list: bgp-speaker-list --sort-key name --sort-key id
        #                               --sort-key asc --sort-key desc
        resources = "bgp_speakers"
        cmd = bgp_speaker.ListSpeakers(test_cli20.MyApp(sys.stdout),
                                       None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_bgp_speaker_limit(self):
        # size (1000) limited list: bgp-speaker-list -P.
        resources = "bgp_speakers"
        cmd = bgp_speaker.ListSpeakers(test_cli20.MyApp(sys.stdout),
                                       None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_show_bgp_speaker(self):
        # Show BGP Speaker: --fields id --fields name myid.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.ShowSpeaker(test_cli20.MyApp(sys.stdout),
                                      None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_delete_bgp_speaker(self):
        # Delete BGP Speaker: bgp_speaker_id.
        resource = 'bgp_speaker'
        cmd = bgp_speaker.DeleteSpeaker(test_cli20.MyApp(sys.stdout),
                                        None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def _test_add_remove_peer(self, action, cmd, args):
        """Add or Remove BGP Peer to/from a BGP Speaker."""
        resource = 'bgp_speaker'
        subcmd = '%s_bgp_peer' % action
        body = {'bgp_peer_id': 'peerid'}
        if action == 'add':
            retval = {'bgp_peer': 'peerid'}
            retval = self.client.serialize(retval)
            expected_code = 200
        else:
            retval = None
            expected_code = 204
        self._test_update_resource_action(resource, cmd, 'myid',
                                          subcmd, args, body, expected_code,
                                          retval)

    def test_add_peer_to_bgp_speaker(self):
        # Add peer to BGP speaker: myid peer_id=peerid
        cmd = bgp_speaker.AddPeerToSpeaker(test_cli20.MyApp(sys.stdout),
                                           None)
        args = ['myid', 'peerid']
        self._test_add_remove_peer('add', cmd, args)

    def test_remove_peer_from_bgp_speaker(self):
        # Remove peer from BGP speaker: myid peer_id=peerid
        cmd = bgp_speaker.RemovePeerFromSpeaker(test_cli20.MyApp(sys.stdout),
                                                None)
        args = ['myid', 'peerid']
        self._test_add_remove_peer('remove', cmd, args)

    def _test_add_remove_network(self, action, cmd, args):
        # Add or Remove network to/from a BGP Speaker.
        resource = 'bgp_speaker'
        subcmd = '%s_gateway_network' % action
        body = {'network_id': 'netid'}
        if action == 'add':
            retval = {'network': 'netid'}
            retval = self.client.serialize(retval)
            expected_code = 200
        else:
            retval = None
            expected_code = 204
        self._test_update_resource_action(resource, cmd, 'myid',
                                          subcmd, args, body, expected_code,
                                          retval)

    def test_add_network_to_bgp_speaker(self):
        # Add peer to BGP speaker: myid network_id=netid
        cmd = bgp_speaker.AddNetworkToSpeaker(test_cli20.MyApp(sys.stdout),
                                              None)
        args = ['myid', 'netid']
        self._test_add_remove_network('add', cmd, args)

    def test_remove_network_from_bgp_speaker(self):
        # Remove network from BGP speaker: myid network_id=netid
        cmd = bgp_speaker.RemoveNetworkFromSpeaker(
            test_cli20.MyApp(sys.stdout), None)
        args = ['myid', 'netid']
        self._test_add_remove_network('remove', cmd, args)

    def test_list_routes_advertised_by_a_bgp_speaker(self):
        # Retrieve advertised route list
        resources = 'advertised_routes'
        cmd = bgp_speaker.ListRoutesAdvertisedBySpeaker(
            test_cli20.MyApp(sys.stdout), None)
        bs_id = 'bgp_speaker_id1'
        path = ((self.client.bgp_speaker_path + '/get_advertised_routes') %
                bs_id)
        self._test_list_resources(resources, cmd, base_args=[bs_id],
                                  path=path)
