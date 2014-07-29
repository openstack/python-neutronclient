# Copyright 2011, VMware, Inc.
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
# Borrowed from nova code base, more utilities will be added/borrowed as and
# when needed.

"""Utilities and helper functions."""

import datetime
import json
import logging
import os
import sys

import six

from neutronclient.common import _
from neutronclient.common import exceptions
from neutronclient.openstack.common import strutils


def env(*vars, **kwargs):
    """Returns the first environment variable set.

    if none are non-empty, defaults to '' or keyword arg default.
    """
    for v in vars:
        value = os.environ.get(v)
        if value:
            return value
    return kwargs.get('default', '')


def to_primitive(value):
    if isinstance(value, list) or isinstance(value, tuple):
        o = []
        for v in value:
            o.append(to_primitive(v))
        return o
    elif isinstance(value, dict):
        o = {}
        for k, v in six.iteritems(value):
            o[k] = to_primitive(v)
        return o
    elif isinstance(value, datetime.datetime):
        return str(value)
    elif hasattr(value, 'iteritems'):
        return to_primitive(dict(value.iteritems()))
    elif hasattr(value, '__iter__'):
        return to_primitive(list(value))
    else:
        return value


def dumps(value, indent=None):
    try:
        return json.dumps(value, indent=indent)
    except TypeError:
        pass
    return json.dumps(to_primitive(value))


def loads(s):
    return json.loads(s)


def import_class(import_str):
    """Returns a class from a string including module and class.

    :param import_str: a string representation of the class name
    :rtype: the requested class
    """
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    return getattr(sys.modules[mod_str], class_str)


def get_client_class(api_name, version, version_map):
    """Returns the client class for the requested API version

    :param api_name: the name of the API, e.g. 'compute', 'image', etc
    :param version: the requested API version
    :param version_map: a dict of client classes keyed by version
    :rtype: a client class for the requested API version
    """
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = _("Invalid %(api_name)s client version '%(version)s'. must be "
                "one of: %(map_keys)s")
        msg = msg % {'api_name': api_name, 'version': version,
                     'map_keys': ', '.join(version_map.keys())}
        raise exceptions.UnsupportedVersion(msg)

    return import_class(client_path)


def get_item_properties(item, fields, mixed_case_fields=[], formatters={}):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Tenant, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []

    for field in fields:
        if field in formatters:
            row.append(formatters[field](item))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            if not hasattr(item, field_name) and isinstance(item, dict):
                data = item[field_name]
            else:
                data = getattr(item, field_name, '')
            if data is None:
                data = ''
            row.append(data)
    return tuple(row)


def str2bool(strbool):
    if strbool is None:
        return None
    else:
        return strbool.lower() == 'true'


def str2dict(strdict):
        '''Convert key1=value1,key2=value2,... string into dictionary.

        :param strdict: key1=value1,key2=value2
        '''
        _info = {}
        if not strdict:
            return _info
        for kv_str in strdict.split(","):
            k, v = kv_str.split("=", 1)
            _info.update({k: v})
        return _info


def http_log_req(_logger, args, kwargs):
    if not _logger.isEnabledFor(logging.DEBUG):
        return

    string_parts = ['curl -i']
    for element in args:
        if element in ('GET', 'POST', 'DELETE', 'PUT'):
            string_parts.append(' -X %s' % element)
        else:
            string_parts.append(' %s' % element)

    for element in kwargs['headers']:
        header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
        string_parts.append(header)

    if 'body' in kwargs and kwargs['body']:
        string_parts.append(" -d '%s'" % (kwargs['body']))
    string_parts = safe_encode_list(string_parts)
    _logger.debug("\nREQ: %s\n", "".join(string_parts))


def http_log_resp(_logger, resp, body):
    if not _logger.isEnabledFor(logging.DEBUG):
        return
    _logger.debug("RESP:%(code)s %(headers)s %(body)s\n",
                  {'code': resp.status_code,
                   'headers': resp.headers,
                   'body': body})


def _safe_encode_without_obj(data):
    if isinstance(data, basestring):
        return strutils.safe_encode(data)
    return data


def safe_encode_list(data):
    return map(_safe_encode_without_obj, data)


def safe_encode_dict(data):
    def _encode_item(item):
        k, v = item
        if isinstance(v, list):
            return (k, safe_encode_list(v))
        elif isinstance(v, dict):
            return (k, safe_encode_dict(v))
        return (k, _safe_encode_without_obj(v))

    return dict(map(_encode_item, data.items()))
