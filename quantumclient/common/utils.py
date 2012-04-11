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
import os


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
    if type(value) is type([]) or type(value) is type((None,)):
        o = []
        for v in value:
            o.append(to_primitive(v))
        return o
    elif type(value) is type({}):
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


def dumps(value):
    try:
        return json.dumps(value)
    except TypeError:
        pass
    return json.dumps(to_primitive(value))


def loads(s):
    return json.loads(s)
