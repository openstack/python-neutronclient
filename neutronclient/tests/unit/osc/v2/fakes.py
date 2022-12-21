#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import argparse
from unittest import mock

from cliff import columns as cliff_columns
from osc_lib.tests import utils


class TestNeutronClientOSCV2(utils.TestCommand):

    def setUp(self):
        super(TestNeutronClientOSCV2, self).setUp()
        self.namespace = argparse.Namespace()
        self.app.client_manager.session = mock.Mock()
        self.app.client_manager.neutronclient = mock.Mock()
        self.neutronclient = self.app.client_manager.neutronclient

        self.app.client_manager.network = mock.Mock()
        self.networkclient = self.app.client_manager.network

        self.addCleanup(mock.patch.stopall)

    # TODO(amotoki): Move this to osc_lib
    def assertListItemEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for item_expected, item_actual in zip(expected, actual):
            self.assertItemEqual(item_expected, item_actual)

    # TODO(amotoki): Move this to osc_lib
    def assertItemEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for col_expected, col_actual in zip(expected, actual):
            if isinstance(col_expected, cliff_columns.FormattableColumn):
                self.assertIsInstance(col_actual, col_expected.__class__)
                self.assertEqual(col_expected.human_readable(),
                                 col_actual.human_readable())
            else:
                self.assertEqual(col_expected, col_actual)
