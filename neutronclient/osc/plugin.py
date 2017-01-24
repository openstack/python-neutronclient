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
#

"""OpenStackClient plugin for advanced Networking service."""

import logging

# TODO(rtheis/amotoki): Add functional test infrastructure for OSC
# plugin commands.
# TODO(amotoki): Add and update document on OSC plugin.

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2.0'
API_VERSION_OPTION = 'os_network_api_version'
# NOTE(rtheis): API_NAME must NOT be set to 'network' since
# 'network' is owned by OSC!  The OSC 'network' client uses
# the OpenStack SDK.
API_NAME = 'neutronclient'
API_VERSIONS = {
    '2.0': 'neutronclient.v2_0.client.Client',
    '2': 'neutronclient.v2_0.client.Client',
}


def make_client(instance):
    """Returns an neutron client."""
    neutron_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating neutron client: %s', neutron_client)

    # TODO(amotoki): Check the following arguments need to be passed
    # to neutronclient class. Check keystoneauth code.
    # - endpoint_type (do we need to specify it explicitly?)
    # - auth (session object contains auth. Is it required?)
    client = neutron_client(session=instance.session,
                            region_name=instance.region_name,
                            endpoint_type=instance.interface,
                            insecure=not instance.verify,
                            ca_cert=instance.cacert)
    return client


def build_option_parser(parser):
    """Hook to add global options"""

    # NOTE(amotoki): At now we register no option.
    # OSC itself has an option for Network API version # and we refer to it.
    return parser
