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

import sys

import mock

from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.neutron.v2_0 import subnet
from neutronclient.tests.unit import test_cli20


class CLITestV20SubnetJSON(test_cli20.CLITestV20Base):

    non_admin_status_resources = ['subnet']

    def setUp(self):
        super(CLITestV20SubnetJSON, self).setUp(plurals={'tags': 'tag'})

    def test_create_subnet(self):
        # Create subnet: --gateway gateway netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = '10.10.10.0/24'
        gateway = 'gatewayvalue'
        args = ['--gateway', gateway, netid, cidr, '--description', 'cave']
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, gateway]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   description='cave')

    def test_create_subnet_network_cidr_seperated(self):
        # For positional value, network_id and cidr can be separated.
        # Create subnet: --gateway gateway netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = '10.10.10.0/24'
        gateway = 'gatewayvalue'
        args = [netid, '--gateway', gateway, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, gateway]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_subnet_with_no_gateway(self):
        # Create subnet: --no-gateway netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        args = ['--no-gateway', netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, None]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_subnet_with_segment(self):
        # Create subnet: --segment segment netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = '10.10.10.0/24'
        segment = 'segment'
        args = ['--segment', segment, netid, cidr,
                '--description', 'cave']
        position_names = ['ip_version', 'network_id', 'cidr', 'segment_id']
        position_values = [4, netid, cidr, segment]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   description='cave')

    def test_create_subnet_with_bad_gateway_option(self):
        # Create sbunet: --no-gateway netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        gateway = 'gatewayvalue'
        args = ['--gateway', gateway, '--no-gateway', netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, None]
        self.assertRaises(
            SystemExit, self._test_create_resource,
            resource, cmd, name, myid, args, position_names, position_values)

    def _test_create_resource_and_catch_command_error(self, should_fail,
                                                      *args):
        if should_fail:
            params = {'no_api_call': True,
                      'expected_exception': exceptions.CommandError}
        else:
            params = {}
        self._test_create_resource(*args, **params)

    def test_create_subnet_with_enable_and_disable_dhcp(self):
        # Create subnet: --enable-dhcp and --disable-dhcp.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        position_names = ['ip_version', 'network_id', 'cidr', 'enable_dhcp']
        # enable_dhcp value is appended later inside the loop
        position_values = [4, netid, cidr]
        for enable_dhcp_arg, should_fail in (
                ('--enable-dhcp=False', False),
                ('--enable-dhcp=True', True),
                ('--enable-dhcp', True)
        ):
            tested_args = [enable_dhcp_arg, '--disable-dhcp']
            args = tested_args + [netid, cidr]
            pos_values = position_values + [should_fail]
            self._test_create_resource_and_catch_command_error(
                should_fail,
                resource, cmd, name, myid, args, position_names, pos_values)

    def test_create_subnet_with_multiple_enable_dhcp(self):
        # Create subnet with multiple --enable-dhcp arguments passed.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        position_names = ['ip_version', 'network_id', 'cidr', 'enable_dhcp']
        # enable_dhcp value is appended later inside the loop
        position_values = [4, netid, cidr]

        _ = 'UNUSED_MARKER'
        for tested_args, should_fail, pos_value in (
                (['--enable-dhcp', '--enable-dhcp=True'], False, True),
                (['--enable-dhcp', '--enable-dhcp=False'], True, _),
                (['--enable-dhcp=False', '--enable-dhcp'], True, _),
                (['--enable-dhcp=True', '--enable-dhcp=False'], True, _),
                (['--enable-dhcp=False', '--enable-dhcp=True'], True, _)
        ):
            args = tested_args + [netid, cidr]
            pos_values = position_values + [pos_value]
            self._test_create_resource_and_catch_command_error(
                should_fail,
                resource, cmd, name, myid, args, position_names, pos_values)

    def test_create_subnet_tenant(self):
        # Create subnet: --tenant_id tenantid netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid', netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr']
        position_values = [4, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_tags(self):
        # Create subnet: netid cidr --tags a b.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = [netid, cidr, '--tags', 'a', 'b']
        position_names = ['ip_version', 'network_id', 'cidr']
        position_values = [4, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tags=['a', 'b'])

    def test_create_subnet_allocation_pool(self):
        # Create subnet: --tenant_id tenantid <pool> netid cidr.
        # The <pool> is --allocation_pool start=1.1.1.10,end=1.1.1.20
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--allocation_pool', 'start=1.1.1.10,end=1.1.1.20',
                netid, cidr]
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pool = [{'start': '1.1.1.10', 'end': '1.1.1.20'}]
        position_values = [4, pool, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_allocation_pools(self):
        # Create subnet: --tenant-id tenantid <pools> netid cidr.
        # The <pools> are --allocation_pool start=1.1.1.10,end=1.1.1.20 and
        # --allocation_pool start=1.1.1.30,end=1.1.1.40
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--allocation_pool', 'start=1.1.1.10,end=1.1.1.20',
                '--allocation_pool', 'start=1.1.1.30,end=1.1.1.40',
                netid, cidr]
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pools = [{'start': '1.1.1.10', 'end': '1.1.1.20'},
                 {'start': '1.1.1.30', 'end': '1.1.1.40'}]
        position_values = [4, pools, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_host_route(self):
        # Create subnet: --tenant_id tenantid <host_route> netid cidr.
        # The <host_route> is
        # --host-route destination=172.16.1.0/24,nexthop=1.1.1.20
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--host-route', 'destination=172.16.1.0/24,nexthop=1.1.1.20',
                netid, cidr]
        position_names = ['ip_version', 'host_routes', 'network_id',
                          'cidr']
        route = [{'destination': '172.16.1.0/24', 'nexthop': '1.1.1.20'}]
        position_values = [4, route, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_host_routes(self):
        # Create subnet: --tenant-id tenantid <host_routes> netid cidr.
        # The <host_routes> are
        # --host-route destination=172.16.1.0/24,nexthop=1.1.1.20 and
        # --host-route destination=172.17.7.0/24,nexthop=1.1.1.40
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--host-route', 'destination=172.16.1.0/24,nexthop=1.1.1.20',
                '--host-route', 'destination=172.17.7.0/24,nexthop=1.1.1.40',
                netid, cidr]
        position_names = ['ip_version', 'host_routes', 'network_id',
                          'cidr']
        routes = [{'destination': '172.16.1.0/24', 'nexthop': '1.1.1.20'},
                  {'destination': '172.17.7.0/24', 'nexthop': '1.1.1.40'}]
        position_values = [4, routes, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_dns_nameservers(self):
        # Create subnet: --tenant-id tenantid <dns-nameservers> netid cidr.
        # The <dns-nameservers> are
        # --dns-nameserver 1.1.1.20 and --dns-nameserver 1.1.1.40
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--dns-nameserver', '1.1.1.20',
                '--dns-nameserver', '1.1.1.40',
                netid, cidr]
        position_names = ['ip_version', 'dns_nameservers', 'network_id',
                          'cidr']
        nameservers = ['1.1.1.20', '1.1.1.40']
        position_values = [4, nameservers, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_with_use_default_subnetpool(self):
        # Create subnet: --tenant-id tenantid --use-default-subnetpool \
        #     netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--use-default-subnetpool',
                netid, cidr]
        position_names = ['ip_version', 'use_default_subnetpool', 'network_id',
                          'cidr']
        position_values = [4, True, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_with_disable_dhcp(self):
        # Create subnet: --tenant-id tenantid --disable-dhcp netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--disable-dhcp',
                netid, cidr]
        position_names = ['ip_version', 'enable_dhcp', 'network_id',
                          'cidr']
        position_values = [4, False, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_merge_single_plurar(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--allocation-pool', 'start=1.1.1.10,end=1.1.1.20',
                netid, cidr,
                '--allocation-pools', 'list=true', 'type=dict',
                'start=1.1.1.30,end=1.1.1.40']
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pools = [{'start': '1.1.1.10', 'end': '1.1.1.20'},
                 {'start': '1.1.1.30', 'end': '1.1.1.40'}]
        position_values = [4, pools, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_merge_plurar(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                netid, cidr,
                '--allocation-pools', 'list=true', 'type=dict',
                'start=1.1.1.30,end=1.1.1.40']
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pools = [{'start': '1.1.1.30', 'end': '1.1.1.40'}]
        position_values = [4, pools, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_merge_single_single(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--allocation-pool', 'start=1.1.1.10,end=1.1.1.20',
                netid, cidr,
                '--allocation-pool',
                'start=1.1.1.30,end=1.1.1.40']
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pools = [{'start': '1.1.1.10', 'end': '1.1.1.20'},
                 {'start': '1.1.1.30', 'end': '1.1.1.40'}]
        position_values = [4, pools, netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_max_v4_cidr(self):
        # Create subnet: --gateway gateway netid cidr.
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = '192.168.0.1/32'
        gateway = 'gatewayvalue'
        args = ['--gateway', gateway, netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, gateway]
        with mock.patch.object(cmd.log, 'warning') as mock_warning:
            self._test_create_resource(resource, cmd, name, myid, args,
                                       position_names, position_values)
        mock_warning.assert_called_once_with(mock.ANY,
                                             {'ip': 4, 'cidr': '/32'})

    def test_create_subnet_with_ipv6_ra_mode(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '6',
                '--ipv6-ra-mode', 'dhcpv6-stateful',
                netid, cidr]
        position_names = ['ip_version', 'ipv6_ra_mode',
                          'network_id', 'cidr']
        position_values = [6, 'dhcpv6-stateful', netid, cidr]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_with_ipv6_address_mode(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '6',
                '--ipv6-address-mode', 'dhcpv6-stateful',
                netid, cidr]
        position_names = ['ip_version', 'ipv6_address_mode',
                          'network_id', 'cidr']
        position_values = [6, 'dhcpv6-stateful', netid, cidr]

        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_with_ipv6_modes(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '6',
                '--ipv6-address-mode', 'slaac',
                '--ipv6-ra-mode', 'slaac',
                netid, cidr]
        position_names = ['ip_version', 'ipv6_address_mode',
                          'ipv6_ra_mode', 'network_id', 'cidr']
        position_values = [6, 'slaac', 'slaac', netid, cidr]

        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_subnet_with_ipv6_ra_mode_ipv4(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '4',
                '--ipv6-ra-mode', 'slaac',
                netid, cidr]
        position_names = ['ip_version', 'ipv6_ra_mode',
                          'network_id', 'cidr']
        position_values = [4, None, netid, cidr]
        self._test_create_resource(
            resource, cmd, name, myid, args, position_names,
            position_values, tenant_id='tenantid',
            no_api_call=True, expected_exception=exceptions.CommandError)

    def test_create_subnet_with_ipv6_address_mode_ipv4(self):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '4',
                '--ipv6-address-mode', 'slaac',
                netid, cidr]
        position_names = ['ip_version', 'ipv6_address_mode',
                          'network_id', 'cidr']
        position_values = [4, None, netid, cidr]
        self._test_create_resource(
            resource, cmd, name, myid, args, position_names,
            position_values, tenant_id='tenantid',
            no_api_call=True, expected_exception=exceptions.CommandError)

    @mock.patch.object(neutronV20, 'find_resource_by_name_or_id')
    def test_create_subnet_with_subnetpool_ipv6_and_ip_ver_ignored(
            self, mock_find_resource):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '4',
                '--subnetpool', 'subnetpool_id',
                netid]
        position_names = ['ip_version', 'network_id', 'subnetpool_id']
        position_values = [6, netid, 'subnetpool_id']
        mock_find_resource.return_value = {
            'id': 'subnetpool_id', 'ip_version': 6}
        self._test_create_resource(
            resource, cmd, name, myid, args, position_names,
            position_values, tenant_id='tenantid')
        mock_find_resource.assert_called_once_with(
            self.client, 'subnetpool', 'subnetpool_id')

    @mock.patch.object(neutronV20, 'find_resource_by_name_or_id')
    def test_create_subnet_with_subnetpool_ipv4_with_cidr_wildcard(
            self, mock_find_resource):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrwildcard'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '4',
                '--ipv6-address-mode', 'slaac',
                '--subnetpool', 'subnetpool_id',
                netid, cidr]
        position_names = ['ip_version', 'ipv6_address_mode',
                          'network_id', 'subnetpool_id', 'cidr']
        position_values = [4, None, netid, 'subnetpool_id', cidr]
        mock_find_resource.return_value = {'id': 'subnetpool_id',
                                           'ip_version': 4}
        self._test_create_resource(
            resource, cmd, name, myid, args, position_names,
            position_values, tenant_id='tenantid',
            no_api_call=True, expected_exception=exceptions.CommandError)
        mock_find_resource.assert_called_once_with(
            self.client, 'subnetpool', 'subnetpool_id')

    @mock.patch.object(neutronV20, 'find_resource_by_name_or_id')
    def test_create_subnet_with_subnetpool_ipv4_with_prefixlen(
            self, mock_find_resource):
        resource = 'subnet'
        cmd = subnet.CreateSubnet(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--tenant_id', 'tenantid',
                '--ip-version', '4',
                '--ipv6-address-mode', 'slaac',
                '--subnetpool', 'subnetpool_id',
                '--prefixlen', '31',
                netid]
        position_names = ['ip_version', 'ipv6_address_mode',
                          'network_id', 'subnetpool_id']
        position_values = [4, None, netid, 'subnetpool_id']
        mock_find_resource.return_value = {'id': 'subnetpool_id',
                                           'ip_version': 4}
        self._test_create_resource(
            resource, cmd, name, myid, args, position_names,
            position_values, tenant_id='tenantid',
            no_api_call=True, expected_exception=exceptions.CommandError)
        mock_find_resource.assert_called_once_with(
            self.client, 'subnetpool', 'subnetpool_id')

    def test_list_subnets_detail(self):
        # List subnets: -D.
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_subnets_tags(self):
        # List subnets: -- --tags a b.
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_subnets_detail_tags(self):
        # List subnets: -D -- --tags a b.
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_subnets_fields(self):
        # List subnets: --fields a --fields b -- --fields c d.
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def test_list_subnets_pagination(self):
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_subnets_sort(self):
        # List subnets: --sort-key name --sort-key id --sort-key asc
        # --sort-key desc
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_subnets_limit(self):
        # List subnets: -P.
        resources = "subnets"
        cmd = subnet.ListSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_update_subnet(self):
        # Update subnet: myid --name myname --tags a b.
        resource = 'subnet'
        cmd = subnet.UpdateSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--description', 'cavern',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'],
                                    'description': 'cavern'})

    def test_update_subnet_allocation_pools(self):
        # Update subnet: myid --name myname --tags a b.
        resource = 'subnet'
        cmd = subnet.UpdateSubnet(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--allocation-pool',
                                    'start=1.2.0.2,end=1.2.0.127'],
                                   {'allocation_pools': [{'start': '1.2.0.2',
                                                          'end': '1.2.0.127'}]}
                                   )

    def test_update_subnet_enable_disable_dhcp(self):
        # Update sbunet: --enable-dhcp and --disable-dhcp.
        resource = 'subnet'
        cmd = subnet.UpdateSubnet(test_cli20.MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError,
                          self._test_update_resource,
                          resource, cmd, 'myid',
                          ['myid', '--name', 'myname', '--enable-dhcp',
                           '--disable-dhcp'], {'name': 'myname', })

    def test_show_subnet(self):
        # Show subnet: --fields id --fields name myid.
        resource = 'subnet'
        cmd = subnet.ShowSubnet(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_delete_subnet(self):
        # Delete subnet: subnetid.
        resource = 'subnet'
        cmd = subnet.DeleteSubnet(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
