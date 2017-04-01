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

import argparse
import functools
import hashlib
import logging
import os

from oslo_utils import encodeutils
from oslo_utils import importutils
import six

from neutronclient._i18n import _
from neutronclient.common import exceptions

SENSITIVE_HEADERS = ('X-Auth-Token',)


def env(*vars, **kwargs):
    """Returns the first environment variable set.

    If none are non-empty, defaults to '' or keyword arg default.
    """
    for v in vars:
        value = os.environ.get(v)
        if value:
            return value
    return kwargs.get('default', '')


def convert_to_uppercase(string):
    return string.upper()


def convert_to_lowercase(string):
    return string.lower()


def get_client_class(api_name, version, version_map):
    """Returns the client class for the requested API version.

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

    return importutils.import_class(client_path)


def get_item_properties(item, fields, mixed_case_fields=(), formatters=None):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Tenant, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    if formatters is None:
        formatters = {}

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
    return strbool.lower() == 'true'


def str2dict(strdict, required_keys=None, optional_keys=None):
    """Convert key1=value1,key2=value2,... string into dictionary.

    :param strdict: string in the form of key1=value1,key2=value2
    :param required_keys: list of required keys. All keys in this list must be
                       specified. Otherwise ArgumentTypeError will be raised.
                       If this parameter is unspecified, no required key check
                       will be done.
    :param optional_keys: list of optional keys.
                       This parameter is used for valid key check.
                       When at least one of required_keys and optional_keys,
                       a key must be a member of either of required_keys or
                       optional_keys. Otherwise, ArgumentTypeError will be
                       raised. When both required_keys and optional_keys are
                       unspecified, no valid key check will be done.
    """
    result = {}
    if strdict:
        i = 0
        kvlist = []
        for kv in strdict.split(','):
            if '=' in kv:
                kvlist.append(kv)
                i += 1
            elif i == 0:
                msg = _("missing value for key '%s'")
                raise argparse.ArgumentTypeError(msg % kv)
            else:
                kvlist[i-1] = "%s,%s" % (kvlist[i-1], kv)
        for kv in kvlist:
            key, sep, value = kv.partition('=')
            if not sep:
                msg = _("invalid key-value '%s', expected format: key=value")
                raise argparse.ArgumentTypeError(msg % kv)
            result[key] = value
    valid_keys = set(required_keys or []) | set(optional_keys or [])
    if valid_keys:
        invalid_keys = [k for k in result if k not in valid_keys]
        if invalid_keys:
            msg = _("Invalid key(s) '%(invalid_keys)s' specified. "
                    "Valid key(s): '%(valid_keys)s'.")
            raise argparse.ArgumentTypeError(
                msg % {'invalid_keys': ', '.join(sorted(invalid_keys)),
                       'valid_keys': ', '.join(sorted(valid_keys))})
    if required_keys:
        not_found_keys = [k for k in required_keys if k not in result]
        if not_found_keys:
            msg = _("Required key(s) '%s' not specified.")
            raise argparse.ArgumentTypeError(msg % ', '.join(not_found_keys))
    return result


def str2dict_type(optional_keys=None, required_keys=None):
    return functools.partial(str2dict,
                             optional_keys=optional_keys,
                             required_keys=required_keys)


def http_log_req(_logger, args, kwargs):
    if not _logger.isEnabledFor(logging.DEBUG):
        return

    string_parts = ['curl -i']
    for element in args:
        if element in ('GET', 'POST', 'DELETE', 'PUT'):
            string_parts.append(' -X %s' % element)
        else:
            string_parts.append(' %s' % element)

    for (key, value) in six.iteritems(kwargs['headers']):
        if key in SENSITIVE_HEADERS:
            v = value.encode('utf-8')
            h = hashlib.sha1(v)
            d = h.hexdigest()
            value = "{SHA1}%s" % d
        header = ' -H "%s: %s"' % (key, value)
        string_parts.append(header)

    if 'body' in kwargs and kwargs['body']:
        string_parts.append(" -d '%s'" % (kwargs['body']))
    req = encodeutils.safe_encode("".join(string_parts))
    _logger.debug("REQ: %s", req)


def http_log_resp(_logger, resp, body):
    if not _logger.isEnabledFor(logging.DEBUG):
        return
    _logger.debug("RESP: %(code)s %(headers)s %(body)s",
                  {'code': resp.status_code,
                   'headers': resp.headers,
                   'body': body})


def _safe_encode_without_obj(data):
    if isinstance(data, six.string_types):
        return encodeutils.safe_encode(data)
    return data


def safe_encode_list(data):
    return list(map(_safe_encode_without_obj, data))


def safe_encode_dict(data):
    def _encode_item(item):
        k, v = item
        if isinstance(v, list):
            return (k, safe_encode_list(v))
        elif isinstance(v, dict):
            return (k, safe_encode_dict(v))
        return (k, _safe_encode_without_obj(v))

    return dict(list(map(_encode_item, data.items())))


def add_boolean_argument(parser, name, **kwargs):
    for keyword in ('metavar', 'choices'):
        kwargs.pop(keyword, None)
    default = kwargs.pop('default', argparse.SUPPRESS)
    parser.add_argument(
        name,
        metavar='{True,False}',
        choices=['True', 'true', 'False', 'false'],
        default=default,
        **kwargs)
