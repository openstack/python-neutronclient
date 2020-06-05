# Copyright (c) 2019 SUSE Linux Products GmbH
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

from unittest import mock

from neutronclient.osc.v2.subnet_onboard import subnet_onboard
from neutronclient.tests.unit.osc.v2 import fakes as test_fakes


def _get_id(client, id_or_name, resource):
    return id_or_name


class TestNetworkOnboardSubnets(test_fakes.TestNeutronClientOSCV2):

    def setUp(self):
        super(TestNetworkOnboardSubnets, self).setUp()
        mock.patch(
            'neutronclient.osc.v2.subnet_onboard.subnet_onboard._get_id',
            new=_get_id).start()

        self.network_id = 'my_network_id'
        self.subnetpool_id = 'my_subnetpool_id'

        # Get the command object to test
        self.cmd = subnet_onboard.NetworkOnboardSubnets(self.app,
                                                        self.namespace)

    def test_options(self):
        arglist = [
            self.network_id,
            self.subnetpool_id
        ]
        verifylist = [
            ('network', self.network_id),
            ('subnetpool', self.subnetpool_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.neutronclient.onboard_network_subnets.assert_called_once_with(
            self.subnetpool_id, {'network_id': self.network_id})
