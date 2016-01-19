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

import sys

from neutronclient.neutron.v2_0 import network_ip_availability
from neutronclient.tests.unit import test_cli20


class CLITestV20NetworkIPAvailability(test_cli20.CLITestV20Base):

    id_field = 'network_id'

    def _test_list_network_ip_availability(self, args, query):
        resources = "network_ip_availabilities"
        cmd = network_ip_availability.ListIpAvailability(test_cli20.MyApp
                                                         (sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  base_args=args,
                                  query=query)

    def test_list_network_ip_availability(self):
        self._test_list_network_ip_availability(args=None,
                                                query='ip_version=4')

    def test_list_network_ip_availability_ipv6(self):
        self._test_list_network_ip_availability(
            args=['--ip-version', '6'], query='ip_version=6')

    def test_list_network_ip_availability_net_id_and_ipv4(self):
        self._test_list_network_ip_availability(
            args=['--ip-version', '4', '--network-id', 'myid'],
            query='ip_version=4&network_id=myid')

    def test_list_network_ip_availability_net_name_and_tenant_id(self):
        self._test_list_network_ip_availability(
            args=['--network-name', 'foo', '--tenant-id', 'mytenant'],
            query='network_name=foo&tenant_id=mytenant&ip_version=4')

    def test_show_network_ip_availability(self):
        resource = "network_ip_availability"
        cmd = network_ip_availability.ShowIpAvailability(
            test_cli20.MyApp(sys.stdout), None)
        self._test_show_resource(resource, cmd, self.test_id,
                                 args=[self.test_id])
