# Copyright 2013 OpenStack LLC.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import testtools

from quantumclient.common import utils


class UtilsTest(testtools.TestCase):
    def test_safe_encode_list(self):
        o = object()
        unicode_text = u'\u7f51\u7edc'
        l = ['abc', unicode_text, unicode_text.encode('utf-8'), o]
        expected = ['abc', unicode_text.encode('utf-8'),
                    unicode_text.encode('utf-8'), o]
        self.assertEqual(utils.safe_encode_list(l), expected)

    def test_safe_encode_dict(self):
        o = object()
        unicode_text = u'\u7f51\u7edc'
        d = {'test1': unicode_text,
             'test2': [unicode_text, o],
             'test3': o,
             'test4': {'test5': unicode_text},
             'test6': unicode_text.encode('utf-8')}
        expected = {'test1': unicode_text.encode('utf-8'),
                    'test2': [unicode_text.encode('utf-8'), o],
                    'test3': o,
                    'test4': {'test5': unicode_text.encode('utf-8')},
                    'test6': unicode_text.encode('utf-8')}
        self.assertEqual(utils.safe_encode_dict(d), expected)
