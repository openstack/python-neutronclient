# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011, Nicira Networks, Inc.
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
# @author: Somik Behera, Nicira Networks, Inc.

"""Utilities and helper functions."""

import datetime
import json
import logging
import os
import sys

from quantumclient.common import exceptions


def env(*vars, **kwargs):
    """
    returns the first environment variable set
    if none are non-empty, defaults to '' or keyword arg default
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
        for k, v in value.iteritems():
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
    """Returns a class from a string including module and class

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
        msg = "Invalid %s client version '%s'. must be one of: %s" % (
              (api_name, version, ', '.join(version_map.keys())))
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
        '''@param strdict: key1=value1,key2=value2'''
        _info = {}
        for kv_str in strdict.split(","):
            k, v = kv_str.split("=", 1)
            _info.update({k: v})
        return _info


def http_log(_logger, args, kwargs, resp, body):
        if not _logger.isEnabledFor(logging.DEBUG):
            return

        string_parts = ['curl -i']
        for element in args:
            if element in ('GET', 'POST'):
                string_parts.append(' -X %s' % element)
            else:
                string_parts.append(' %s' % element)

        for element in kwargs['headers']:
            header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
            string_parts.append(header)

        _logger.debug("REQ: %s\n" % "".join(string_parts))
        if 'body' in kwargs and kwargs['body']:
            _logger.debug("REQ BODY: %s\n" % (kwargs['body']))
        _logger.debug("RESP:%s\n", resp)
        _logger.debug("RESP BODY:%s\n", body)
