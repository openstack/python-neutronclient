# Copyright 2016 NEC Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_serialization import jsonutils
from oslo_utils import uuidutils
import yaml

from neutronclient.tests.functional import base


class TestCLIFormatter(base.ClientTestBase):

    def setUp(self):
        super(TestCLIFormatter, self).setUp()
        self.net_name = 'net-%s' % uuidutils.generate_uuid()
        self.addCleanup(self.neutron, 'net-delete %s' % self.net_name)

    def _create_net(self, fmt, col_attrs):
        params = ['-c %s' % attr for attr in col_attrs]
        params.append('-f %s' % fmt)
        params.append(self.net_name)
        param_string = ' '.join(params)
        return self.neutron('net-create', params=param_string)

    def test_net_create_with_json_formatter(self):
        result = self._create_net('json', ['name', 'admin_state_up'])
        self.assertDictEqual({'name': self.net_name,
                              'admin_state_up': True},
                             jsonutils.loads(result))

    def test_net_create_with_yaml_formatter(self):
        result = self._create_net('yaml', ['name', 'admin_state_up'])
        self.assertDictEqual({'name': self.net_name,
                              'admin_state_up': True},
                             yaml.load(result))

    def test_net_create_with_value_formatter(self):
        # NOTE(amotoki): In 'value' formatter, there is no guarantee
        # in the order of attribute, so we use one attribute in this test.
        result = self._create_net('value', ['name'])
        self.assertEqual(self.net_name, result.strip())

    def test_net_create_with_shell_formatter(self):
        result = self._create_net('shell', ['name', 'admin_state_up'])
        result_lines = set(result.strip().split('\n'))
        self.assertSetEqual(set(['name="%s"' % self.net_name,
                                 'admin_state_up="True"']),
                            result_lines)
