# Copyright 2013 OpenStack Foundation.
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

from oslo_serialization import jsonutils
import six

from neutronclient._i18n import _
from neutronclient.common import exceptions as exception


if six.PY3:
    long = int


class ActionDispatcher(object):
    """Maps method name to local methods through action name."""

    def dispatch(self, *args, **kwargs):
        """Find and call local method."""
        action = kwargs.pop('action', 'default')
        action_method = getattr(self, str(action), self.default)
        return action_method(*args, **kwargs)

    def default(self, data):
        raise NotImplementedError()


class DictSerializer(ActionDispatcher):
    """Default request body serialization."""

    def serialize(self, data, action='default'):
        return self.dispatch(data, action=action)

    def default(self, data):
        return ""


class JSONDictSerializer(DictSerializer):
    """Default JSON request body serialization."""

    def default(self, data):
        def sanitizer(obj):
            return six.text_type(obj)
        return jsonutils.dumps(data, default=sanitizer)


class TextDeserializer(ActionDispatcher):
    """Default request body deserialization."""

    def deserialize(self, datastring, action='default'):
        return self.dispatch(datastring, action=action)

    def default(self, datastring):
        return {}


class JSONDeserializer(TextDeserializer):

    def _from_json(self, datastring):
        try:
            return jsonutils.loads(datastring)
        except ValueError:
            msg = _("Cannot understand JSON")
            raise exception.MalformedResponseBody(reason=msg)

    def default(self, datastring):
        return {'body': self._from_json(datastring)}


# NOTE(maru): this class is duplicated from neutron.wsgi
class Serializer(object):
    """Serializes and deserializes dictionaries to certain MIME types."""

    def __init__(self, metadata=None):
        """Create a serializer based on the given WSGI environment.

        'metadata' is an optional dict mapping MIME types to information
        needed to serialize a dictionary to that type.

        """
        self.metadata = metadata or {}

    def _get_serialize_handler(self, content_type):
        handlers = {
            'application/json': JSONDictSerializer(),
        }

        try:
            return handlers[content_type]
        except Exception:
            raise exception.InvalidContentType(content_type=content_type)

    def serialize(self, data):
        """Serialize a dictionary into the specified content type."""
        return self._get_serialize_handler("application/json").serialize(data)

    def deserialize(self, datastring):
        """Deserialize a string to a dictionary.

        The string must be in the format of a supported MIME type.
        """
        return self.get_deserialize_handler("application/json").deserialize(
            datastring)

    def get_deserialize_handler(self, content_type):
        handlers = {
            'application/json': JSONDeserializer(),
        }

        try:
            return handlers[content_type]
        except Exception:
            raise exception.InvalidContentType(content_type=content_type)
