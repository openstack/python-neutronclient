#    (c) Copyright 2013 Hewlett-Packard Development Company, L.P.
#    All Rights Reserved.
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
from neutronclient.neutron.v2_0.vpn import ipsec_site_connection
from neutronclient.tests.unit import test_cli20


class CLITestV20IPsecSiteConnectionJSON(test_cli20.CLITestV20Base):

    # TODO(pcm): Remove, once peer-cidr is deprecated completely
    def test_create_ipsec_site_connection_all_params_using_peer_cidrs(self):
        # ipsecsite-connection-create all params using peer CIDRs.
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        tenant_id = 'mytenant_id'
        name = 'connection1'
        my_id = 'my_id'
        peer_address = '192.168.2.10'
        peer_id = '192.168.2.10'
        psk = 'abcd'
        mtu = '1500'
        initiator = 'bi-directional'
        vpnservice_id = 'vpnservice_id'
        ikepolicy_id = 'ikepolicy_id'
        ipsecpolicy_id = 'ipsecpolicy_id'
        peer_cidrs = ['192.168.3.0/24', '192.168.2.0/24']
        admin_state = True
        description = 'my-vpn-connection'
        dpd = 'action=restart,interval=30,timeout=120'

        args = ['--tenant-id', tenant_id,
                '--peer-address', peer_address, '--peer-id', peer_id,
                '--psk', psk, '--initiator', initiator,
                '--vpnservice-id', vpnservice_id,
                '--ikepolicy-id', ikepolicy_id, '--name', name,
                '--ipsecpolicy-id', ipsecpolicy_id, '--mtu', mtu,
                '--description', description,
                '--peer-cidr', '192.168.3.0/24',
                '--peer-cidr', '192.168.2.0/24',
                '--dpd', dpd]

        position_names = ['name', 'tenant_id', 'admin_state_up',
                          'peer_address', 'peer_id', 'peer_cidrs',
                          'psk', 'mtu', 'initiator', 'description',
                          'vpnservice_id', 'ikepolicy_id',
                          'ipsecpolicy_id']

        position_values = [name, tenant_id, admin_state, peer_address,
                           peer_id, peer_cidrs, psk, mtu,
                           initiator, description,
                           vpnservice_id, ikepolicy_id, ipsecpolicy_id]
        extra_body = {
            'dpd': {
                'action': 'restart',
                'interval': 30,
                'timeout': 120,
            },
        }

        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values,
                                   extra_body=extra_body)

    def test_create_ipsec_site_conn_all_params(self):
        # ipsecsite-connection-create all params using endpoint groups.
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        tenant_id = 'mytenant_id'
        name = 'connection1'
        my_id = 'my_id'
        peer_address = '192.168.2.10'
        peer_id = '192.168.2.10'
        psk = 'abcd'
        mtu = '1500'
        initiator = 'bi-directional'
        vpnservice_id = 'vpnservice_id'
        ikepolicy_id = 'ikepolicy_id'
        ipsecpolicy_id = 'ipsecpolicy_id'
        local_ep_group = 'local-epg'
        peer_ep_group = 'peer-epg'
        admin_state = True
        description = 'my-vpn-connection'
        dpd = 'action=restart,interval=30,timeout=120'

        args = ['--tenant-id', tenant_id,
                '--peer-address', peer_address, '--peer-id', peer_id,
                '--psk', psk, '--initiator', initiator,
                '--vpnservice-id', vpnservice_id,
                '--ikepolicy-id', ikepolicy_id, '--name', name,
                '--ipsecpolicy-id', ipsecpolicy_id, '--mtu', mtu,
                '--description', description,
                '--local-ep-group', local_ep_group,
                '--peer-ep-group', peer_ep_group,
                '--dpd', dpd]

        position_names = ['name', 'tenant_id', 'admin_state_up',
                          'peer_address', 'peer_id', 'psk', 'mtu',
                          'local_ep_group_id', 'peer_ep_group_id',
                          'initiator', 'description',
                          'vpnservice_id', 'ikepolicy_id',
                          'ipsecpolicy_id']

        position_values = [name, tenant_id, admin_state, peer_address,
                           peer_id, psk, mtu, local_ep_group,
                           peer_ep_group, initiator, description,
                           vpnservice_id, ikepolicy_id, ipsecpolicy_id]
        extra_body = {
            'dpd': {
                'action': 'restart',
                'interval': 30,
                'timeout': 120,
            },
        }

        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values,
                                   extra_body=extra_body)

    def test_create_ipsec_site_connection_with_limited_params(self):
        # ipsecsite-connection-create with limited params.
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        tenant_id = 'mytenant_id'
        my_id = 'my_id'
        peer_address = '192.168.2.10'
        peer_id = '192.168.2.10'
        psk = 'abcd'
        mtu = '1500'
        initiator = 'bi-directional'
        vpnservice_id = 'vpnservice_id'
        ikepolicy_id = 'ikepolicy_id'
        ipsecpolicy_id = 'ipsecpolicy_id'
        local_ep_group = 'local-epg'
        peer_ep_group = 'peer-epg'
        admin_state = True

        args = ['--tenant-id', tenant_id,
                '--peer-address', peer_address,
                '--peer-id', peer_id,
                '--psk', psk,
                '--vpnservice-id', vpnservice_id,
                '--ikepolicy-id', ikepolicy_id,
                '--ipsecpolicy-id', ipsecpolicy_id,
                '--local-ep-group', local_ep_group,
                '--peer-ep-group', peer_ep_group]

        position_names = ['tenant_id', 'admin_state_up',
                          'peer_address', 'peer_id',
                          'local_ep_group_id', 'peer_ep_group_id',
                          'psk', 'mtu', 'initiator',
                          'vpnservice_id', 'ikepolicy_id',
                          'ipsecpolicy_id']

        position_values = [tenant_id, admin_state, peer_address, peer_id,
                           local_ep_group, peer_ep_group, psk, mtu, initiator,
                           vpnservice_id, ikepolicy_id, ipsecpolicy_id]

        self._test_create_resource(resource, cmd, None, my_id, args,
                                   position_names, position_values)

    def _test_create_failure(self, additional_args=None, expected_exc=None):
        # Helper to test failure of IPSec site-to-site creation failure.
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        tenant_id = 'mytenant_id'
        my_id = 'my_id'
        peer_address = '192.168.2.10'
        peer_id = '192.168.2.10'
        psk = 'abcd'
        mtu = '1500'
        initiator = 'bi-directional'
        vpnservice_id = 'vpnservice_id'
        ikepolicy_id = 'ikepolicy_id'
        ipsecpolicy_id = 'ipsecpolicy_id'
        admin_state = True

        args = ['--tenant-id', tenant_id,
                '--peer-address', peer_address,
                '--peer-id', peer_id,
                '--psk', psk,
                '--vpnservice-id', vpnservice_id,
                '--ikepolicy-id', ikepolicy_id,
                '--ipsecpolicy-id', ipsecpolicy_id]
        if additional_args is not None:
            args += additional_args
        position_names = ['tenant_id', 'admin_state_up', 'peer_address',
                          'peer_id', 'psk', 'mtu', 'initiator',
                          'local_ep_group_id', 'peer_ep_group_id',
                          'vpnservice_id', 'ikepolicy_id', 'ipsecpolicy_id']

        position_values = [tenant_id, admin_state, peer_address, peer_id, psk,
                           mtu, initiator, None, None, vpnservice_id,
                           ikepolicy_id, ipsecpolicy_id]
        if not expected_exc:
            expected_exc = exceptions.CommandError
        self.assertRaises(expected_exc,
                          self._test_create_resource,
                          resource, cmd, None, my_id, args,
                          position_names, position_values)

    def test_fail_create_with_invalid_mtu(self):
        # ipsecsite-connection-create with invalid dpd values.
        bad_mtu = ['--mtu', '67']
        self._test_create_failure(bad_mtu)

    def test_fail_create_with_invalid_dpd_keys(self):
        bad_dpd_key = ['--dpd', 'act=restart,interval=30,time=120']
        self._test_create_failure(bad_dpd_key, SystemExit)

    def test_fail_create_with_invalid_dpd_values(self):
        bad_dpd_values = ['--dpd', 'action=hold,interval=30,timeout=-1']
        self._test_create_failure(bad_dpd_values)

    def test_fail_create_missing_endpoint_groups_or_cidr(self):
        # Must provide either endpoint groups or peer cidrs.
        self._test_create_failure()

    def test_fail_create_missing_peer_endpoint_group(self):
        # Fails if dont have both endpoint groups - missing peer.
        self._test_create_failure(['--local-ep-group', 'local-epg'])

    def test_fail_create_missing_local_endpoint_group(self):
        # Fails if dont have both endpoint groups - missing local.
        self._test_create_failure(['--peer-ep-group', 'peer-epg'])

    def test_fail_create_when_both_endpoints_and_peer_cidr(self):
        # Cannot intermix endpoint groups and peer CIDRs for create.
        additional_args = ['--local-ep-group', 'local-epg',
                           '--peer-ep-group', 'peer-epg',
                           '--peer-cidr', '10.2.0.0/24']
        self._test_create_failure(additional_args)

    def test_list_ipsec_site_connection(self):
        # ipsecsite-connection-list.
        resources = "ipsec_site_connections"
        cmd = ipsec_site_connection.ListIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        self._test_list_resources(resources, cmd, True)

    def test_list_ipsec_site_connection_pagination(self):
        # ipsecsite-connection-list.
        resources = "ipsec_site_connections"
        cmd = ipsec_site_connection.ListIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_ipsec_site_connection_sort(self):
        # ipsecsite-connection-list.
        # --sort-key name --sort-key id --sort-key asc --sort-key desc
        resources = "ipsec_site_connections"
        cmd = ipsec_site_connection.ListIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_ipsec_site_connection_limit(self):
        # ipsecsite-connection-list -P.
        resources = "ipsec_site_connections"
        cmd = ipsec_site_connection.ListIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_delete_ipsec_site_connection(self):
        # ipsecsite-connection-delete my-id.
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.DeleteIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)

    def test_update_ipsec_site_connection(self):
        # ipsecsite-connection-update  myid --name Branch-new --tags a b.
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.UpdateIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'Branch-new',
                                    '--tags', 'a', 'b'],
                                   {'name': 'Branch-new',
                                    'tags': ['a', 'b'], })
        # ipsecsite-connection-update myid --mtu 69 --initiator response-only
        # --peer-id '192.168.2.11' --peer-ep-group 'update-grp'
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--mtu', '69',
                                    '--initiator', 'response-only',
                                    '--peer-id', '192.168.2.11',
                                    '--peer-ep-group', 'update-grp'],
                                   {'mtu': '69',
                                    'initiator': 'response-only',
                                    'peer_id': '192.168.2.11',
                                    'peer_ep_group_id': 'update-grp', },)

    def test_show_ipsec_site_connection_id(self):
        # ipsecsite-connection-show test_id."""
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.ShowIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'])

    def test_show_ipsec_site_connection_id_name(self):
        # ipsecsite-connection-show."""
        resource = 'ipsec_site_connection'
        cmd = ipsec_site_connection.ShowIPsecSiteConnection(
            test_cli20.MyApp(sys.stdout), None
        )
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])
