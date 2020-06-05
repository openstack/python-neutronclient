# Copyright 2017 FUJITSU LIMITED
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

import collections
import copy
from unittest import mock
import uuid


class FakeLogging(object):

    def create(self, attrs={}):
        """Create a fake network logs

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A OrderedDict faking the network log
        """
        self.ordered.update(attrs)
        return copy.deepcopy(self.ordered)

    def bulk_create(self, attrs=None, count=2):
        """Create multiple fake network logs

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of network logs to fake
        :return:
            A list of dictionaries faking the network logs
        """
        return [self.create(attrs=attrs) for i in range(0, count)]

    def get(self, attrs=None, count=2):
        """Create multiple fake network logs

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of network logs to fake
        :return:
            A list of dictionaries faking the network log
        """
        if attrs is None:
            self.attrs = self.bulk_create(count=count)
        return mock.Mock(side_effect=attrs)


class NetworkLog(FakeLogging):
    """Fake one or more network log"""

    def __init__(self):
        super(NetworkLog, self).__init__()
        self.ordered = collections.OrderedDict((
            ('id', 'log-id-' + uuid.uuid4().hex),
            ('description', 'my-desc-' + uuid.uuid4().hex),
            ('enabled', False),
            ('name', 'my-log-' + uuid.uuid4().hex),
            ('target_id', None),
            ('project_id', 'project-id-' + uuid.uuid4().hex),
            ('resource_id', None),
            ('resource_type', 'security_group'),
            ('event', 'all'),
        ))
