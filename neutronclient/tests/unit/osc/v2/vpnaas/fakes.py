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
import uuid

import mock


class FakeVPNaaS(object):

    def create(self, attrs={}):
        """Create a fake vpnaas resources

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A OrderedDict faking the vpnaas resource
        """
        self.ordered.update(attrs)
        return copy.deepcopy(self.ordered)

    def bulk_create(self, attrs=None, count=2):
        """Create multiple fake vpnaas resources

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of vpnaas resources to fake
        :return:
            A list of dictionaries faking the vpnaas resources
        """
        return [self.create(attrs=attrs) for i in range(0, count)]

    def get(self, attrs=None, count=2):
        """Get multiple fake vpnaas resources

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of vpnaas resources to fake
        :return:
            A list of dictionaries faking the vpnaas resource
        """
        if attrs is None:
            self.attrs = self.bulk_create(count=count)
        return mock.Mock(side_effect=attrs)


class IKEPolicy(FakeVPNaaS):
    """Fake one or more IKE policies"""

    def __init__(self):
        super(IKEPolicy, self).__init__()
        self.ordered = collections.OrderedDict((
            ('id', 'ikepolicy-id-' + uuid.uuid4().hex),
            ('name', 'my-ikepolicy-' + uuid.uuid4().hex),
            ('auth_algorithm', 'sha1'),
            ('encryption_algorithm', 'aes-128'),
            ('ike_version', 'v1'),
            ('pfs', 'group5'),
            ('description', 'my-desc-' + uuid.uuid4().hex),
            ('phase1_negotiation_mode', 'main'),
            ('tenant_id', 'tenant-id-' + uuid.uuid4().hex),
            ('lifetime', {'units': 'seconds', 'value': 3600}),
        ))


class IPSecPolicy(FakeVPNaaS):
    """Fake one or more IPsec policies"""

    def __init__(self):
        super(IPSecPolicy, self).__init__()
        self.ordered = collections.OrderedDict((
            ('id', 'ikepolicy-id-' + uuid.uuid4().hex),
            ('name', 'my-ikepolicy-' + uuid.uuid4().hex),
            ('auth_algorithm', 'sha1'),
            ('encapsulation_mode', 'tunnel'),
            ('transform_protocol', 'esp'),
            ('encryption_algorithm', 'aes-128'),
            ('pfs', 'group5'),
            ('description', 'my-desc-' + uuid.uuid4().hex),
            ('tenant_id', 'tenant-id-' + uuid.uuid4().hex),
            ('lifetime', {'units': 'seconds', 'value': 3600}),
        ))


class VPNService(FakeVPNaaS):
    """Fake one or more VPN services"""

    def __init__(self):
        super(VPNService, self).__init__()
        self.ordered = collections.OrderedDict((
            ('id', 'vpnservice-id-' + uuid.uuid4().hex),
            ('name', 'my-vpnservice-' + uuid.uuid4().hex),
            ('router_id', 'router-id-' + uuid.uuid4().hex),
            ('subnet_id', 'subnet-id-' + uuid.uuid4().hex),
            ('flavor_id', 'flavor-id-' + uuid.uuid4().hex),
            ('admin_state_up', True),
            ('status', 'ACTIVE'),
            ('description', 'my-desc-' + uuid.uuid4().hex),
            ('tenant_id', 'tenant-id-' + uuid.uuid4().hex),
        ))


class EndpointGroup(FakeVPNaaS):
    """Fake one or more Endpoint Groups"""

    def __init__(self):
        super(EndpointGroup, self).__init__()
        self.ordered = collections.OrderedDict((
            ('id', 'ep-group-id-' + uuid.uuid4().hex),
            ('name', 'my-ep-group-' + uuid.uuid4().hex),
            ('type', 'cidr'),
            ('endpoints', ['10.0.0.0/24', '20.0.0.0/24']),
            ('description', 'my-desc-' + uuid.uuid4().hex),
            ('tenant_id', 'tenant-id-' + uuid.uuid4().hex),
        ))


class IPsecSiteConnection(object):
    """Fake one or more IPsec site connections"""
    @staticmethod
    def create_conn(attrs=None):
        """Create a fake IPsec conn.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A Dictionary with id, name, peer_address, auth_mode, status,
            tenant_id, peer_cidrs, vpnservice_id, ipsecpolicy_id,
            ikepolicy_id, mtu, initiator, admin_state_up, description,
            psk, route_mode, local_id, peer_id, local_ep_group_id,
            peer_ep_group_id
        """
        attrs = attrs or {}

        # Set default attributes.
        conn_attrs = {
            'id': 'ipsec-site-conn-id-' + uuid.uuid4().hex,
            'name': 'my-ipsec-site-conn-' + uuid.uuid4().hex,
            'peer_address': '192.168.2.10',
            'auth_mode': '',
            'status': '',
            'tenant_id': 'tenant-id-' + uuid.uuid4().hex,
            'peer_cidrs': [],
            'vpnservice_id': 'vpnservice-id-' + uuid.uuid4().hex,
            'ipsecpolicy_id': 'ipsecpolicy-id-' + uuid.uuid4().hex,
            'ikepolicy_id': 'ikepolicy-id-' + uuid.uuid4().hex,
            'mtu': 1500,
            'initiator': 'bi-directional',
            'admin_state_up': True,
            'description': 'my-vpn-connection',
            'psk': 'abcd',
            'route_mode': '',
            'local_id': '',
            'peer_id': '192.168.2.10',
            'local_ep_group_id': 'local-ep-group-id-' + uuid.uuid4().hex,
            'peer_ep_group_id': 'peer-ep-group-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        conn_attrs.update(attrs)
        return copy.deepcopy(conn_attrs)
