# Copyright 2016 Cisco Systems
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

from neutronclient.neutron.v2_0 import purge
from neutronclient.tests.unit import test_cli20


class CLITestV20Purge(test_cli20.CLITestV20Base):

    def setUp(self):
        super(CLITestV20Purge, self).setUp()
        self.resource_types = ['floatingip', 'port', 'router',
                               'network', 'security_group']

    def _generate_resources_dict(self, value=0):
        resources_dict = {}
        resources_dict['true'] = value
        for resource_type in self.resource_types:
            resources_dict[resource_type] = value
        return resources_dict

    def _verify_suffix(self, resources, message):
        for resource, value in resources.items():
            if value > 0:
                suffix = list('%(value)d %(resource)s' %
                              {'value': value, 'resource': resource})
                if value != 1:
                    suffix.append('s')
                suffix = ''.join(suffix)
                self.assertIn(suffix, message)
            else:
                self.assertNotIn(resource, message)

    def _verify_message(self, message, deleted, failed):
        message = message.split('.')
        success_prefix = "Deleted "
        failure_prefix = "The following resources could not be deleted: "
        if not deleted['true']:
            for msg in message:
                self.assertNotIn(success_prefix, msg)
            message = message[0]
            if not failed['true']:
                expected = 'Tenant has no supported resources'
                self.assertEqual(expected, message)
            else:
                self.assertIn(failure_prefix, message)
                self._verify_suffix(failed, message)
        else:
            resources_deleted = message[0]
            self.assertIn(success_prefix, resources_deleted)
            self._verify_suffix(deleted, resources_deleted)
            if failed['true']:
                resources_failed = message[1]
                self.assertIn(failure_prefix, resources_failed)
                self._verify_suffix(failed, resources_failed)
            else:
                for msg in message:
                    self.assertNotIn(failure_prefix, msg)

    def _verify_result(self, my_purge, deleted, failed):
        message = my_purge._build_message(deleted, failed, failed['true'])
        self._verify_message(message, deleted, failed)

    def test_build_message(self):
        my_purge = purge.Purge(test_cli20.MyApp(sys.stdout), None)

        # Verify message when tenant has no supported resources
        deleted = self._generate_resources_dict()
        failed = self._generate_resources_dict()
        self._verify_result(my_purge, deleted, failed)

        # Verify message when tenant has supported resources,
        # and they are all deleteable
        deleted = self._generate_resources_dict(1)
        self._verify_result(my_purge, deleted, failed)

        # Verify message when tenant has supported resources,
        # and some are not deleteable
        failed = self._generate_resources_dict(1)
        self._verify_result(my_purge, deleted, failed)

        # Verify message when tenant has supported resources,
        # and all are not deleteable
        deleted = self._generate_resources_dict()
        self._verify_result(my_purge, deleted, failed)
