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

from neutronclient.neutron.v2_0 import availability_zone as az
from neutronclient.tests.unit import test_cli20


class CLITestV20Agent(test_cli20.CLITestV20Base):
    def test_list_agents(self):
        contents = {'availability_zones': [{'name': 'zone1',
                                            'resource': 'network',
                                            'state': 'available'},
                                           {'name': 'zone2',
                                            'resource': 'router',
                                            'state': 'unavailable'}]}
        args = ['-f', 'json']
        resources = "availability_zones"

        cmd = az.ListAvailabilityZone(test_cli20.MyApp(sys.stdout), None)
        self._test_list_columns(cmd, resources, contents, args)
