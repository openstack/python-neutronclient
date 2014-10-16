# Copyright 2012 OpenStack Foundation.
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

import abc
try:
    import json
except ImportError:
    import simplejson as json
import logging
import os

from keystoneclient import access
from keystoneclient.auth.identity.base import BaseIdentityPlugin
import requests
import six

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.i18n import _

_logger = logging.getLogger(__name__)

if os.environ.get('NEUTRONCLIENT_DEBUG'):
    ch = logging.StreamHandler()
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(ch)
    _requests_log_level = logging.DEBUG
else:
    _requests_log_level = logging.WARNING

logging.getLogger("requests").setLevel(_requests_log_level)


@six.add_metaclass(abc.ABCMeta)
class AbstractHTTPClient(object):

    USER_AGENT = 'python-neutronclient'
    CONTENT_TYPE = 'application/json'

    def request(self, url, method, body=None, content_type=None, headers=None,
                **kwargs):
        """Request without authentication."""

        headers = headers or {}
        content_type = content_type or self.CONTENT_TYPE
        headers.setdefault('Accept', content_type)
        if body:
            headers.setdefault('Content-Type', content_type)

        return self._request(url, method, body=body, headers=headers, **kwargs)

    @abc.abstractmethod
    def do_request(self, url, method, **kwargs):
        """Request with authentication."""

    @abc.abstractmethod
    def _request(self, url, method, body=None, headers=None, **kwargs):
        """Request without authentication nor headers population."""


class HTTPClient(AbstractHTTPClient):
    """Handles the REST calls and responses, include authentication."""

    def __init__(self, username=None, user_id=None,
                 tenant_name=None, tenant_id=None,
                 password=None, auth_url=None,
                 token=None, region_name=None, timeout=None,
                 endpoint_url=None, insecure=False,
                 endpoint_type='publicURL',
                 auth_strategy='keystone', ca_cert=None, log_credentials=False,
                 service_type='network',
                 **kwargs):

        self.username = username
        self.user_id = user_id
        self.tenant_name = tenant_name
        self.tenant_id = tenant_id
        self.password = password
        self.auth_url = auth_url.rstrip('/') if auth_url else None
        self.service_type = service_type
        self.endpoint_type = endpoint_type
        self.region_name = region_name
        self.timeout = timeout
        self.auth_token = token
        self.auth_tenant_id = None
        self.auth_user_id = None
        self.endpoint_url = endpoint_url
        self.auth_strategy = auth_strategy
        self.log_credentials = log_credentials
        if insecure:
            self.verify_cert = False
        else:
            self.verify_cert = ca_cert if ca_cert else True

    def _cs_request(self, *args, **kwargs):
        kargs = {}
        kargs.setdefault('headers', kwargs.get('headers', {}))
        kargs['headers']['User-Agent'] = self.USER_AGENT

        if 'body' in kwargs:
            kargs['body'] = kwargs['body']
        args = utils.safe_encode_list(args)
        kargs = utils.safe_encode_dict(kargs)

        if self.log_credentials:
            log_kargs = kargs
        else:
            log_kargs = self._strip_credentials(kargs)

        utils.http_log_req(_logger, args, log_kargs)
        try:
            resp, body = self.request(*args, **kargs)
        except requests.exceptions.SSLError as e:
            raise exceptions.SslCertificateValidationError(reason=e)
        except Exception as e:
            # Wrap the low-level connection error (socket timeout, redirect
            # limit, decompression error, etc) into our custom high-level
            # connection exception (it is excepted in the upper layers of code)
            _logger.debug("throwing ConnectionFailed : %s", e)
            raise exceptions.ConnectionFailed(reason=e)
        utils.http_log_resp(_logger, resp, body)
        if resp.status_code == 401:
            raise exceptions.Unauthorized(message=body)
        return resp, body

    def _strip_credentials(self, kwargs):
        if kwargs.get('body') and self.password:
            log_kwargs = kwargs.copy()
            log_kwargs['body'] = kwargs['body'].replace(self.password,
                                                        'REDACTED')
            return log_kwargs
        else:
            return kwargs

    def authenticate_and_fetch_endpoint_url(self):
        if not self.auth_token:
            self.authenticate()
        elif not self.endpoint_url:
            self.endpoint_url = self._get_endpoint_url()

    def _request(self, url, method, body=None, headers=None, **kwargs):
        headers = headers or {}
        headers['User-Agent'] = self.USER_AGENT

        resp = requests.request(
            method,
            url,
            data=body,
            headers=headers,
            verify=self.verify_cert,
            timeout=self.timeout,
            **kwargs)

        return resp, resp.text

    def do_request(self, url, method, **kwargs):
        self.authenticate_and_fetch_endpoint_url()
        # Perform the request once. If we get a 401 back then it
        # might be because the auth token expired, so try to
        # re-authenticate and try again. If it still fails, bail.
        try:
            kwargs.setdefault('headers', {})
            if self.auth_token is None:
                self.auth_token = ""
            kwargs['headers']['X-Auth-Token'] = self.auth_token
            resp, body = self._cs_request(self.endpoint_url + url, method,
                                          **kwargs)
            return resp, body
        except exceptions.Unauthorized:
            self.authenticate()
            kwargs.setdefault('headers', {})
            kwargs['headers']['X-Auth-Token'] = self.auth_token
            resp, body = self._cs_request(
                self.endpoint_url + url, method, **kwargs)
            return resp, body

    def _extract_service_catalog(self, body):
        """Set the client's service catalog from the response data."""
        self.auth_ref = access.AccessInfo.factory(body=body)
        self.service_catalog = self.auth_ref.service_catalog
        self.auth_token = self.auth_ref.auth_token
        self.auth_tenant_id = self.auth_ref.tenant_id
        self.auth_user_id = self.auth_ref.user_id

        if not self.endpoint_url:
            self.endpoint_url = self.service_catalog.url_for(
                attr='region', filter_value=self.region_name,
                service_type=self.service_type,
                endpoint_type=self.endpoint_type)

    def _authenticate_keystone(self):
        if self.user_id:
            creds = {'userId': self.user_id,
                     'password': self.password}
        else:
            creds = {'username': self.username,
                     'password': self.password}

        if self.tenant_id:
            body = {'auth': {'passwordCredentials': creds,
                             'tenantId': self.tenant_id, }, }
        else:
            body = {'auth': {'passwordCredentials': creds,
                             'tenantName': self.tenant_name, }, }

        if self.auth_url is None:
            raise exceptions.NoAuthURLProvided()

        token_url = self.auth_url + "/tokens"
        resp, resp_body = self._cs_request(token_url, "POST",
                                           body=json.dumps(body),
                                           content_type="application/json",
                                           allow_redirects=True)
        if resp.status_code != 200:
            raise exceptions.Unauthorized(message=resp_body)
        if resp_body:
            try:
                resp_body = json.loads(resp_body)
            except ValueError:
                pass
        else:
            resp_body = None
        self._extract_service_catalog(resp_body)

    def _authenticate_noauth(self):
        if not self.endpoint_url:
            message = _('For "noauth" authentication strategy, the endpoint '
                        'must be specified either in the constructor or '
                        'using --os-url')
            raise exceptions.Unauthorized(message=message)

    def authenticate(self):
        if self.auth_strategy == 'keystone':
            self._authenticate_keystone()
        elif self.auth_strategy == 'noauth':
            self._authenticate_noauth()
        else:
            err_msg = _('Unknown auth strategy: %s') % self.auth_strategy
            raise exceptions.Unauthorized(message=err_msg)

    def _get_endpoint_url(self):
        if self.auth_url is None:
            raise exceptions.NoAuthURLProvided()

        url = self.auth_url + '/tokens/%s/endpoints' % self.auth_token
        try:
            resp, body = self._cs_request(url, "GET")
        except exceptions.Unauthorized:
            # rollback to authenticate() to handle case when neutron client
            # is initialized just before the token is expired
            self.authenticate()
            return self.endpoint_url

        body = json.loads(body)
        for endpoint in body.get('endpoints', []):
            if (endpoint['type'] == 'network' and
                    endpoint.get('region') == self.region_name):
                if self.endpoint_type not in endpoint:
                    raise exceptions.EndpointTypeNotFound(
                        type_=self.endpoint_type)
                return endpoint[self.endpoint_type]

        raise exceptions.EndpointNotFound()

    def get_auth_info(self):
        return {'auth_token': self.auth_token,
                'auth_tenant_id': self.auth_tenant_id,
                'auth_user_id': self.auth_user_id,
                'endpoint_url': self.endpoint_url}


class SessionClient(AbstractHTTPClient):

    def __init__(self,
                 session,
                 auth,
                 interface=None,
                 service_type=None,
                 region_name=None):

        self.session = session
        self.auth = auth
        self.interface = interface
        self.service_type = service_type
        self.region_name = region_name
        self.auth_token = None
        self.endpoint_url = None

    def _request(self, url, method, body=None, headers=None, **kwargs):
        kwargs.setdefault('user_agent', self.USER_AGENT)
        kwargs.setdefault('auth', self.auth)
        kwargs.setdefault('authenticated', False)
        kwargs.setdefault('raise_exc', False)

        endpoint_filter = kwargs.setdefault('endpoint_filter', {})
        endpoint_filter.setdefault('interface', self.interface)
        endpoint_filter.setdefault('service_type', self.service_type)
        endpoint_filter.setdefault('region_name', self.region_name)

        kwargs = utils.safe_encode_dict(kwargs)
        resp = self.session.request(url, method, data=body, headers=headers,
                                    **kwargs)
        return resp, resp.text

    def do_request(self, url, method, **kwargs):
        kwargs.setdefault('authenticated', True)
        return self.request(url, method, **kwargs)

    def authenticate(self):
        # This method is provided for backward compatibility only.
        # We only care about setting the service endpoint.
        self.endpoint_url = self.session.get_endpoint(
            self.auth,
            service_type=self.service_type,
            region_name=self.region_name,
            interface=self.interface)

    def authenticate_and_fetch_endpoint_url(self):
        # This method is provided for backward compatibility only.
        # We only care about setting the service endpoint.
        self.authenticate()

    def get_auth_info(self):
        # This method is provided for backward compatibility only.
        if not isinstance(self.auth, BaseIdentityPlugin):
            msg = ('Auth info not available. Auth plugin is not an identity '
                   'auth plugin.')
            raise exceptions.NeutronClientException(message=msg)
        access_info = self.auth.get_access(self.session)
        endpoint_url = self.auth.get_endpoint(self.session,
                                              service_type=self.service_type,
                                              region_name=self.region_name,
                                              interface=self.interface)
        return {'auth_token': access_info.auth_token,
                'auth_tenant_id': access_info.tenant_id,
                'auth_user_id': access_info.user_id,
                'endpoint_url': endpoint_url}


# FIXME(bklei): Should refactor this to use kwargs and only
# explicitly list arguments that are not None.
def construct_http_client(username=None,
                          user_id=None,
                          tenant_name=None,
                          tenant_id=None,
                          password=None,
                          auth_url=None,
                          token=None,
                          region_name=None,
                          timeout=None,
                          endpoint_url=None,
                          insecure=False,
                          endpoint_type='publicURL',
                          log_credentials=None,
                          auth_strategy='keystone',
                          ca_cert=None,
                          service_type='network',
                          session=None,
                          auth=None):

    if session:
        return SessionClient(session=session,
                             auth=auth,
                             interface=endpoint_type,
                             service_type=service_type,
                             region_name=region_name)
    else:
        # FIXME(bklei): username and password are now optional. Need
        # to test that they were provided in this mode.  Should also
        # refactor to use kwargs.
        return HTTPClient(username=username,
                          password=password,
                          tenant_id=tenant_id,
                          tenant_name=tenant_name,
                          user_id=user_id,
                          auth_url=auth_url,
                          token=token,
                          endpoint_url=endpoint_url,
                          insecure=insecure,
                          timeout=timeout,
                          region_name=region_name,
                          endpoint_type=endpoint_type,
                          service_type=service_type,
                          ca_cert=ca_cert,
                          log_credentials=log_credentials,
                          auth_strategy=auth_strategy)
