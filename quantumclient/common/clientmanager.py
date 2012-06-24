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

"""Manage access to the clients, including authenticating when needed.
"""

import logging

from quantumclient.common import exceptions as exc

from quantumclient.quantum import client as quantum_client
from quantumclient.client import HTTPClient
LOG = logging.getLogger(__name__)


class ClientCache(object):
    """Descriptor class for caching created client handles.
    """

    def __init__(self, factory):
        self.factory = factory
        self._handle = None

    def __get__(self, instance, owner):
        # Tell the ClientManager to login to keystone
        if self._handle is None:
            self._handle = self.factory(instance)
        return self._handle


class ClientManager(object):
    """Manages access to API clients, including authentication.
    """
    quantum = ClientCache(quantum_client.make_client)

    def __init__(self, token=None, url=None,
                 auth_url=None,
                 tenant_name=None, tenant_id=None,
                 username=None, password=None,
                 region_name=None,
                 api_version=None,
                 auth_strategy=None
                 ):
        self._token = token
        self._url = url
        self._auth_url = auth_url
        self._tenant_name = tenant_name
        self._tenant_id = tenant_id
        self._username = username
        self._password = password
        self._region_name = region_name
        self._api_version = api_version
        self._service_catalog = None
        self._auth_strategy = auth_strategy
        return

    def initialize(self):
        if not self._url:
            httpclient = HTTPClient(username=self._username,
                                    tenant_name=self._tenant_name,
                                    password=self._password,
                                    region_name=self._region_name,
                                    auth_url=self._auth_url)
            httpclient.authenticate()
            # Populate other password flow attributes
            self._token = httpclient.auth_token
            self._url = httpclient.endpoint_url
