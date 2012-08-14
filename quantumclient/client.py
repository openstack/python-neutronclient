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

try:
    import json
except ImportError:
    import simplejson as json
import logging
import os
import urlparse
# Python 2.5 compat fix
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl

import httplib2

from quantumclient.common import exceptions
from quantumclient.common import utils

_logger = logging.getLogger(__name__)

if 'QUANTUMCLIENT_DEBUG' in os.environ and os.environ['QUANTUMCLIENT_DEBUG']:
    ch = logging.StreamHandler()
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(ch)


class ServiceCatalog(object):
    """Helper methods for dealing with a Keystone Service Catalog."""

    def __init__(self, resource_dict):
        self.catalog = resource_dict

    def get_token(self):
        """Fetch token details fron service catalog"""
        token = {'id': self.catalog['access']['token']['id'],
                 'expires': self.catalog['access']['token']['expires'], }
        try:
            token['user_id'] = self.catalog['access']['user']['id']
            token['tenant_id'] = (
                self.catalog['access']['token']['tenant']['id'])
        except:
            # just leave the tenant and user out if it doesn't exist
            pass
        return token

    def url_for(self, attr=None, filter_value=None,
                service_type='network', endpoint_type='adminURL'):
        """Fetch the admin URL from the Quantum service for
        a particular endpoint attribute. If none given, return
        the first. See tests for sample service catalog."""

        catalog = self.catalog['access'].get('serviceCatalog', [])
        matching_endpoints = []
        for service in catalog:
            if service['type'] != service_type:
                continue

            endpoints = service['endpoints']
            for endpoint in endpoints:
                if not filter_value or endpoint.get(attr) == filter_value:
                    matching_endpoints.append(endpoint)

        if not matching_endpoints:
            raise exceptions.EndpointNotFound()
        elif len(matching_endpoints) > 1:
            raise exceptions.AmbiguousEndpoints(message=matching_endpoints)
        else:
            return matching_endpoints[0][endpoint_type]


class HTTPClient(httplib2.Http):
    """Handles the REST calls and responses, include authn"""

    USER_AGENT = 'python-quantumclient'

    def __init__(self, username=None, tenant_name=None,
                 password=None, auth_url=None,
                 token=None, region_name=None, timeout=None,
                 endpoint_url=None, insecure=False,
                 auth_strategy='keystone', **kwargs):
        super(HTTPClient, self).__init__(timeout=timeout)
        self.username = username
        self.tenant_name = tenant_name
        self.password = password
        self.auth_url = auth_url.rstrip('/') if auth_url else None
        self.region_name = region_name
        self.auth_token = token
        self.token_retrieved = False
        self.content_type = 'application/json'
        self.endpoint_url = endpoint_url
        self.auth_strategy = auth_strategy
        # httplib2 overrides
        self.force_exception_to_status_code = True
        self.disable_ssl_certificate_validation = insecure

    def _cs_request(self, *args, **kwargs):
        kargs = {}
        kargs.setdefault('headers', kwargs.get('headers', {}))
        kargs['headers']['User-Agent'] = self.USER_AGENT

        if 'content_type' in kwargs:
            kargs['headers']['Content-Type'] = kwargs['content_type']
            kargs['headers']['Accept'] = kwargs['content_type']
        else:
            kargs['headers']['Content-Type'] = self.content_type
            kargs['headers']['Accept'] = self.content_type

        if 'body' in kwargs:
            kargs['body'] = kwargs['body']

        resp, body = self.request(*args, **kargs)

        utils.http_log(_logger, args, kargs, resp, body)
        status_code = self.get_status_code(resp)
        if status_code == 401:
            raise exceptions.Unauthorized(message=body)
        elif status_code == 403:
            raise exceptions.Forbidden(message=body)
        return resp, body

    def do_request(self, url, method, **kwargs):
        if not self.endpoint_url:
            self.authenticate()

        # Perform the request once. If we get a 401 back then it
        # might be because the auth token expired, so try to
        # re-authenticate and try again. If it still fails, bail.
        try:
            if self.auth_token:
                kwargs.setdefault('headers', {})
                kwargs['headers']['X-Auth-Token'] = self.auth_token
            resp, body = self._cs_request(self.endpoint_url + url, method,
                                          **kwargs)
            return resp, body
        except exceptions.Unauthorized as ex:
            if not self.endpoint_url or self.token_retrieved:
                self.authenticate()
                if self.auth_token:
                    kwargs.setdefault('headers', {})
                    kwargs['headers']['X-Auth-Token'] = self.auth_token
                resp, body = self._cs_request(
                    self.endpoint_url + url, method, **kwargs)
                return resp, body
            else:
                raise ex

    def _extract_service_catalog(self, body):
        """ Set the client's service catalog from the response data. """
        self.service_catalog = ServiceCatalog(body)
        try:
            sc = self.service_catalog.get_token()
            self.auth_token = sc['id']
            self.auth_tenant_id = sc.get('tenant_id')
            self.auth_user_id = sc.get('user_id')
            self.token_retrieved = True
        except KeyError:
            raise exceptions.Unauthorized()
        self.endpoint_url = self.service_catalog.url_for(
            attr='region', filter_value=self.region_name,
            endpoint_type='adminURL')

    def authenticate(self):
        if self.auth_strategy != 'keystone':
            raise exceptions.Unauthorized(message='unknown auth strategy')
        body = {'auth': {'passwordCredentials':
                         {'username': self.username,
                          'password': self.password, },
                         'tenantName': self.tenant_name, }, }

        token_url = self.auth_url + "/tokens"

        # Make sure we follow redirects when trying to reach Keystone
        tmp_follow_all_redirects = self.follow_all_redirects
        self.follow_all_redirects = True
        try:
            resp, body = self._cs_request(token_url, "POST",
                                          body=json.dumps(body),
                                          content_type="application/json")
        finally:
            self.follow_all_redirects = tmp_follow_all_redirects
        status_code = self.get_status_code(resp)
        if status_code != 200:
            raise exceptions.Unauthorized(message=body)
        if body:
            try:
                body = json.loads(body)
            except ValueError:
                pass
        else:
            body = None
        self._extract_service_catalog(body)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status
