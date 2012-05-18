# Copyright 2012 OpenStack LLC.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging
import urlparse


from quantumclient.common import utils

LOG = logging.getLogger(__name__)

API_NAME = 'network'
API_VERSIONS = {
    '1.0': 'quantumclient.Client',
    '1.1': 'quantumclient.ClientV11',
    '2.0': 'quantumclient.v2_0.client.Client',
}


def make_client(instance):
    """Returns an identity service client.
    """
    quantum_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS,
    )
    instance.initialize()
    url = instance._url
    url = url.rstrip("/")
    client_full_name = (quantum_client.__module__ + "." +
                        quantum_client.__name__)
    LOG.debug("we are using client: %s", client_full_name)
    v1x = (client_full_name == API_VERSIONS['1.1'] or
           client_full_name == API_VERSIONS['1.0'])
    if v1x:
        magic_tuple = urlparse.urlsplit(url)
        scheme, netloc, path, query, frag = magic_tuple
        host = magic_tuple.hostname
        port = magic_tuple.port
        use_ssl = scheme.lower().startswith('https')
        client = quantum_client(host=host, port=port, use_ssl=use_ssl)
        client.auth_token = instance._token
        client.logger = LOG
        return client
    else:
        client = quantum_client(username=instance._username,
                                tenant_name=instance._tenant_name,
                                password=instance._password,
                                region_name=instance._region_name,
                                auth_url=instance._auth_url,
                                endpoint_url=url,
                                token=instance._token)
        return client
