#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import copy

import mock
from oslo_utils import uuidutils


class FakeTrunk(object):
    """Fake one or more trunks."""
    @staticmethod
    def create_one_trunk(attrs=None):
        """Create a fake trunk.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A Dictionary with id, name, description, admin_state_up, port_id,
            sub_ports, status and project_id
        """
        attrs = attrs or {}

        # Set default attributes.
        trunk_attrs = {
            'id': 'trunk-id-' + uuidutils.generate_uuid(dashed=False),
            'name': 'trunk-name-' + uuidutils.generate_uuid(dashed=False),
            'description': '',
            'port_id': 'port-' + uuidutils.generate_uuid(dashed=False),
            'admin_state_up': True,
            'project_id': 'project-id-' +
            uuidutils.generate_uuid(dashed=False),
            'status': 'ACTIVE',
            'sub_ports': [{'port_id': 'subport-' +
                           uuidutils.generate_uuid(dashed=False),
                           'segmentation_type': 'vlan',
                           'segmentation_id': 100}],
        }

        # Overwrite default attributes.
        trunk_attrs.update(attrs)
        return copy.deepcopy(trunk_attrs)

    @staticmethod
    def create_trunks(attrs=None, count=2):
        """Create multiple fake trunks.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of routers to fake
        :return:
            A list of dictionaries faking the trunks
        """
        trunks = []
        for i in range(0, count):
            trunks.append(FakeTrunk.create_one_trunk(attrs))

        return trunks

    @staticmethod
    def get_trunks(trunks=None, count=2):
        """Get an iterable Mock object with a list of faked trunks.

        If trunks list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List trunks:
            A list of FakeResource objects faking trunks
        :param int count:
            The number of trunks to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            trunks
        """
        if trunks is None:
            trunks = FakeTrunk.create_trunks(count)
        return mock.Mock(side_effect=trunks)
