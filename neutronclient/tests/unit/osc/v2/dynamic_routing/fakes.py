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

import copy
import uuid

import mock

from neutronclient.tests.unit.osc.v2 import fakes


class TestNeutronDynamicRoutingOSCV2(fakes.TestNeutronClientOSCV2):
    def setUp(self):
        super(TestNeutronDynamicRoutingOSCV2, self).setUp()
        self.neutronclient.find_resource = mock.Mock(
            side_effect=lambda resource, name_or_id, project_id=None,
            cmd_resource=None, parent_id=None, fields=None:
            {'id': name_or_id})


class FakeBgpSpeaker(object):
    """Fake one or more bgp speakers."""

    @staticmethod
    def create_one_bgp_speaker(attrs=None):
        attrs = attrs or {}
        # Set default attributes.
        bgp_speaker_attrs = {
            'peers': [],
            'local_as': 200,
            'advertise_tenant_networks': True,
            'networks': [],
            'ip_version': 4,
            'advertise_floating_ip_host_routes': True,
            'id': uuid.uuid4().hex,
            'name': 'bgp-speaker-' + uuid.uuid4().hex,
            'tenant_id': uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        bgp_speaker_attrs.update(attrs)

        return copy.deepcopy(bgp_speaker_attrs)

    @staticmethod
    def create_bgp_speakers(attrs=None, count=1):
        """Create multiple fake bgp speakers.

        """
        bgp_speakers = []
        for i in range(0, count):
            bgp_speaker = FakeBgpSpeaker.create_one_bgp_speaker(attrs)
            bgp_speakers.append(bgp_speaker)

        return {'bgp_speakers': bgp_speakers}


class FakeBgpPeer(object):
    """Fake one or more bgp peers."""

    @staticmethod
    def create_one_bgp_peer(attrs=None):
        attrs = attrs or {}
        # Set default attributes.
        bgp_peer_attrs = {
            'auth_type': None,
            'peer_ip': '1.1.1.1',
            'remote_as': 100,
            'id': uuid.uuid4().hex,
            'name': 'bgp-peer-' + uuid.uuid4().hex,
            'tenant_id': uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        bgp_peer_attrs.update(attrs)

        return copy.deepcopy(bgp_peer_attrs)

    @staticmethod
    def create_bgp_peers(attrs=None, count=1):
        """Create one or multiple fake bgp peers."""
        bgp_peers = []
        for i in range(0, count):
            bgp_peer = FakeBgpPeer.create_one_bgp_peer(attrs)
            bgp_peers.append(bgp_peer)

        return {'bgp_peers': bgp_peers}
