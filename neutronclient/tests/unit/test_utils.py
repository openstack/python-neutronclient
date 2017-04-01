# Copyright (C) 2013 Yahoo! Inc.
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

import argparse

from oslo_utils import netutils

import testtools

from neutronclient.common import exceptions
from neutronclient.common import utils


class TestUtils(testtools.TestCase):
    def test_string_to_bool_true(self):
        self.assertTrue(utils.str2bool('true'))

    def test_string_to_bool_false(self):
        self.assertFalse(utils.str2bool('false'))

    def test_string_to_bool_None(self):
        self.assertIsNone(utils.str2bool(None))

    def test_string_to_dictionary(self):
        input_str = 'key1=value1,key2=value2'
        expected = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(expected, utils.str2dict(input_str))

    def test_none_string_to_dictionary(self):
        input_str = ''
        expected = {}
        self.assertEqual(expected, utils.str2dict(input_str))
        input_str = None
        expected = {}
        self.assertEqual(expected, utils.str2dict(input_str))

    def test_invalid_string_to_dictionary(self):
        input_str = 'invalid'
        self.assertRaises(argparse.ArgumentTypeError,
                          utils.str2dict, input_str)

    def test_string_with_comma_value_to_dictionary(self):
        input_str = ('opt_name=classless-static-route,'
                     'opt_value=169.254.169.254/32,10.0.0.1')
        expected = {'opt_name': 'classless-static-route',
                    'opt_value': '169.254.169.254/32,10.0.0.1'}
        self.assertEqual(expected, utils.str2dict(input_str))

    def test_str2dict_optional_keys(self):
        self.assertDictEqual({'key1': 'value1'},
                             utils.str2dict('key1=value1',
                                            optional_keys=['key1', 'key2']))
        self.assertDictEqual({'key1': 'value1', 'key2': 'value2'},
                             utils.str2dict('key1=value1,key2=value2',
                                            optional_keys=['key1', 'key2']))
        e = self.assertRaises(argparse.ArgumentTypeError,
                              utils.str2dict,
                              'key1=value1,key2=value2,key3=value3',
                              optional_keys=['key1', 'key2'])
        self.assertEqual("Invalid key(s) 'key3' specified. "
                         "Valid key(s): 'key1, key2'.",
                         str(e))

    def test_str2dict_required_keys(self):
        self.assertDictEqual(
            {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'},
            utils.str2dict('key1=value1,key2=value2,key3=value3',
                           required_keys=['key1', 'key2'],
                           optional_keys=['key3']))
        self.assertDictEqual(
            {'key1': 'value1', 'key2': 'value2'},
            utils.str2dict('key1=value1,key2=value2',
                           required_keys=['key1', 'key2']))
        e = self.assertRaises(argparse.ArgumentTypeError,
                              utils.str2dict, 'key1=value1',
                              required_keys=['key1', 'key2'])
        self.assertEqual("Required key(s) 'key2' not specified.", str(e))

    def test_get_dict_item_properties(self):
        item = {'name': 'test_name', 'id': 'test_id'}
        fields = ('name', 'id')
        actual = utils.get_item_properties(item=item, fields=fields)
        self.assertEqual(('test_name', 'test_id'), actual)

    def test_get_object_item_properties_mixed_case_fields(self):
        class Fake(object):
            def __init__(self):
                self.id = 'test_id'
                self.name = 'test_name'
                self.test_user = 'test'

        fields = ('name', 'id', 'test user')
        mixed_fields = ('test user', 'ID')
        item = Fake()
        actual = utils.get_item_properties(item, fields, mixed_fields)
        self.assertEqual(('test_name', 'test_id', 'test'), actual)

    def test_get_object_item_desired_fields_differ_from_item(self):
        class Fake(object):
            def __init__(self):
                self.id = 'test_id_1'
                self.name = 'test_name'
                self.test_user = 'test'

        fields = ('name', 'id', 'test user')
        item = Fake()
        actual = utils.get_item_properties(item, fields)
        self.assertNotEqual(('test_name', 'test_id', 'test'), actual)

    def test_get_object_item_desired_fields_is_empty(self):
        class Fake(object):
            def __init__(self):
                self.id = 'test_id_1'
                self.name = 'test_name'
                self.test_user = 'test'

        fields = []
        item = Fake()
        actual = utils.get_item_properties(item, fields)
        self.assertEqual((), actual)

    def test_get_object_item_with_formatters(self):
        class Fake(object):
            def __init__(self):
                self.id = 'test_id'
                self.name = 'test_name'
                self.test_user = 'test'

        class FakeCallable(object):
            def __call__(self, *args, **kwargs):
                return 'pass'

        fields = ('name', 'id', 'test user', 'is_public')
        formatters = {'is_public': FakeCallable()}
        item = Fake()
        act = utils.get_item_properties(item, fields, formatters=formatters)
        self.assertEqual(('test_name', 'test_id', 'test', 'pass'), act)

    def test_is_cidr(self):
        self.assertTrue(netutils.is_valid_cidr('10.10.10.0/24'))
        self.assertFalse(netutils.is_valid_cidr('10.10.10..0/24'))
        self.assertFalse(netutils.is_valid_cidr('wrong_cidr_format'))


class ImportClassTestCase(testtools.TestCase):
    def test_get_client_class_invalid_version(self):
        self.assertRaises(
            exceptions.UnsupportedVersion,
            utils.get_client_class, 'image', '2', {'image': '2'})
