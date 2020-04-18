# All Rights Reserved.
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

import sys
from unittest import mock

from oslo_utils import encodeutils
import testtools

from neutronclient._i18n import _
from neutronclient.common import exceptions


class TestExceptions(testtools.TestCase):

    def test_exception_print_with_unicode(self):
        class TestException(exceptions.NeutronException):
            message = _('Exception with %(reason)s')

        multibyte_unicode_string = u'\uff21\uff22\uff23'
        e = TestException(reason=multibyte_unicode_string)

        with mock.patch.object(sys, 'stdout') as mock_stdout:
            print(e)

        exc_str = 'Exception with %s' % multibyte_unicode_string
        mock_stdout.assert_has_calls([mock.call.write(exc_str)])

    def test_exception_message_with_encoded_unicode(self):
        class TestException(exceptions.NeutronException):
            message = _('Exception with %(reason)s')

        multibyte_string = u'\uff21\uff22\uff23'
        multibyte_binary = encodeutils.safe_encode(multibyte_string)
        e = TestException(reason=multibyte_binary)
        self.assertEqual('Exception with %s' % multibyte_string,
                         str(e))
