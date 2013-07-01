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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import datetime
import sys

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


class JSONUtilsTestCase(testtools.TestCase):
    def test_dumps(self):
        self.assertEqual(utils.dumps({'a': 'b'}), '{"a": "b"}')

    def test_dumps_dict_with_date_value(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        res = utils.dumps({1: 'a', 2: x})
        expected = '{"1": "a", "2": "1920-02-03 04:05:06.000007"}'
        self.assertEqual(expected, res)

    def test_dumps_dict_with_spaces(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        res = utils.dumps({1: 'a ', 2: x})
        expected = '{"1": "a ", "2": "1920-02-03 04:05:06.000007"}'
        self.assertEqual(expected, res)

    def test_loads(self):
        self.assertEqual(utils.loads('{"a": "b"}'), {'a': 'b'})


class ToPrimitiveTestCase(testtools.TestCase):
    def test_list(self):
        self.assertEqual(utils.to_primitive([1, 2, 3]), [1, 2, 3])

    def test_empty_list(self):
        self.assertEqual(utils.to_primitive([]), [])

    def test_tuple(self):
        self.assertEqual(utils.to_primitive((1, 2, 3)), [1, 2, 3])

    def test_empty_tuple(self):
        self.assertEqual(utils.to_primitive(()), [])

    def test_dict(self):
        self.assertEqual(
            utils.to_primitive(dict(a=1, b=2, c=3)),
            dict(a=1, b=2, c=3))

    def test_empty_dict(self):
        self.assertEqual(utils.to_primitive({}), {})

    def test_datetime(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        self.assertEqual(
            utils.to_primitive(x),
            '1920-02-03 04:05:06.000007')

    def test_iter(self):
        x = xrange(1, 6)
        self.assertEqual(utils.to_primitive(x), [1, 2, 3, 4, 5])

    def test_iteritems(self):
        d = {'a': 1, 'b': 2, 'c': 3}

        class IterItemsClass(object):
            def iteritems(self):
                return d.iteritems()

        x = IterItemsClass()
        p = utils.to_primitive(x)
        self.assertEqual(p, {'a': 1, 'b': 2, 'c': 3})

    def test_nasties(self):
        def foo():
            pass
        x = [datetime, foo, dir]
        ret = utils.to_primitive(x)
        self.assertEqual(len(ret), 3)

    def test_to_primitive_dict_with_date_value(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        res = utils.to_primitive({'a': x})
        self.assertEqual({'a': '1920-02-03 04:05:06.000007'}, res)


class ImportClassTestCase(testtools.TestCase):
    def test_import_class(self):
        dt = utils.import_class('datetime.datetime')
        self.assertTrue(sys.modules['datetime'].datetime is dt)

    def test_import_bad_class(self):
        self.assertRaises(
            ImportError, utils.import_class,
            'lol.u_mad.brah')

    def test_get_client_class_invalid_version(self):
        self.assertRaises(
            exceptions.UnsupportedVersion,
            utils.get_client_class, 'image', '2', {'image': '2'})
