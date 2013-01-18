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

import httplib
import logging
import time
import urllib

from quantumclient.client import HTTPClient
from quantumclient.common import _
from quantumclient.common import constants
from quantumclient.common import exceptions
from quantumclient.common import serializer


_logger = logging.getLogger(__name__)


def exception_handler_v20(status_code, error_content):
    """ Exception handler for API v2.0 client

        This routine generates the appropriate
        Quantum exception according to the contents of the
        response body

        :param status_code: HTTP error status code
        :param error_content: deserialized body of error response
    """

    quantum_errors = {
        'NetworkNotFound': exceptions.NetworkNotFoundClient,
        'NetworkInUse': exceptions.NetworkInUseClient,
        'PortNotFound': exceptions.PortNotFoundClient,
        'RequestedStateInvalid': exceptions.StateInvalidClient,
        'PortInUse': exceptions.PortInUseClient,
        'AlreadyAttached': exceptions.AlreadyAttachedClient, }

    error_dict = None
    if isinstance(error_content, dict):
        error_dict = error_content.get('QuantumError')
    # Find real error type
    bad_quantum_error_flag = False
    if error_dict:
        # If QuantumError key is found, it will definitely contain
        # a 'message' and 'type' keys?
        try:
            error_type = error_dict['type']
            error_message = (error_dict['message'] + "\n" +
                             error_dict['detail'])
        except Exception:
            bad_quantum_error_flag = True
        if not bad_quantum_error_flag:
            ex = None
            try:
                # raise the appropriate error!
                ex = quantum_errors[error_type](message=error_message)
                ex.args = ([dict(status_code=status_code,
                                 message=error_message)], )
            except Exception:
                pass
            if ex:
                raise ex
        else:
            raise exceptions.QuantumClientException(status_code=status_code,
                                                    message=error_dict)
    else:
        message = None
        if isinstance(error_content, dict):
            message = error_content.get('message', None)
        if message:
            raise exceptions.QuantumClientException(status_code=status_code,
                                                    message=message)

    # If we end up here the exception was not a quantum error
    msg = "%s-%s" % (status_code, error_content)
    raise exceptions.QuantumClientException(status_code=status_code,
                                            message=msg)


class APIParamsCall(object):
    """A Decorator to add support for format and tenant overriding
       and filters
    """
    def __init__(self, function):
        self.function = function

    def __get__(self, instance, owner):
        def with_params(*args, **kwargs):
            _format = instance.format
            if 'format' in kwargs:
                instance.format = kwargs['format']
            ret = self.function(instance, *args, **kwargs)
            instance.format = _format
            return ret
        return with_params


class Client(object):
    """Client for the OpenStack Quantum v2.0 API.

    :param string username: Username for authentication. (optional)
    :param string password: Password for authentication. (optional)
    :param string token: Token for authentication. (optional)
    :param string tenant_name: Tenant name. (optional)
    :param string auth_url: Keystone service endpoint for authorization.
    :param string region_name: Name of a region to select when choosing an
                               endpoint from the service catalog.
    :param string endpoint_url: A user-supplied endpoint URL for the quantum
                            service.  Lazy-authentication is possible for API
                            service calls if endpoint is set at
                            instantiation.(optional)
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    :param insecure: ssl certificate validation. (optional)

    Example::

        >>> from quantumclient.v2_0 import client
        >>> quantum = client.Client(username=USER,
                                     password=PASS,
                                     tenant_name=TENANT_NAME,
                                     auth_url=KEYSTONE_URL)

        >>> nets = quantum.list_networks()
        ...

    """

    networks_path = "/networks"
    network_path = "/networks/%s"
    ports_path = "/ports"
    port_path = "/ports/%s"
    subnets_path = "/subnets"
    subnet_path = "/subnets/%s"
    quotas_path = "/quotas"
    quota_path = "/quotas/%s"
    exts_path = "/extensions"
    ext_path = "/extensions/%s"
    routers_path = "/routers"
    router_path = "/routers/%s"
    floatingips_path = "/floatingips"
    floatingip_path = "/floatingips/%s"
    security_groups_path = "/security-groups"
    security_group_path = "/security-groups/%s"
    security_group_rules_path = "/security-group-rules"
    security_group_rule_path = "/security-group-rules/%s"
    vips_path = "/lb/vips"
    vip_path = "/lb/vips/%s"
    pools_path = "/lb/pools"
    pool_path = "/lb/pools/%s"
    pool_path_stats = "/lb/pools/%s/stats"
    members_path = "/lb/members"
    member_path = "/lb/members/%s"
    health_monitors_path = "/lb/health_monitors"
    health_monitor_path = "/lb/health_monitors/%s"
    associate_pool_health_monitors_path = "/lb/pools/%s/health_monitors"
    disassociate_pool_health_monitors_path = (
        "/lb/pools/%(pool)s/health_monitors/%(health_monitor)s")

    # API has no way to report plurals, so we have to hard code them
    EXTED_PLURALS = {'routers': 'router',
                     'floatingips': 'floatingip',
                     'service_types': 'service_type',
                     'service_definitions': 'service_definition',
                     'security_groups': 'security_group',
                     'security_group_rules': 'security_group_rule',
                     'vips': 'vip',
                     'pools': 'pool',
                     'members': 'member',
                     'health_monitors': 'health_monitor',
                     'quotas': 'quota',
                     }

    def get_attr_metadata(self):
        if self.format == 'json':
            return {}
        old_request_format = self.format
        self.format = 'json'
        exts = self.list_extensions()['extensions']
        self.format = old_request_format
        ns = dict([(ext['alias'], ext['namespace']) for ext in exts])
        self.EXTED_PLURALS.update(constants.PLURALS)
        return {'plurals': self.EXTED_PLURALS,
                'xmlns': constants.XML_NS_V20,
                constants.EXT_NS: ns}

    @APIParamsCall
    def get_quotas_tenant(self, **_params):
        """Fetch tenant info in server's context for
        following quota operation."""
        return self.get(self.quota_path % 'tenant', params=_params)

    @APIParamsCall
    def list_quotas(self, **_params):
        """Fetch all tenants' quotas."""
        return self.get(self.quotas_path, params=_params)

    @APIParamsCall
    def show_quota(self, tenant_id, **_params):
        """Fetch information of a certain tenant's quotas."""
        return self.get(self.quota_path % (tenant_id), params=_params)

    @APIParamsCall
    def update_quota(self, tenant_id, body=None):
        """Update a tenant's quotas."""
        return self.put(self.quota_path % (tenant_id), body=body)

    @APIParamsCall
    def delete_quota(self, tenant_id):
        """Delete the specified tenant's quota values."""
        return self.delete(self.quota_path % (tenant_id))

    @APIParamsCall
    def list_extensions(self, **_params):
        """Fetch a list of all exts on server side."""
        return self.get(self.exts_path, params=_params)

    @APIParamsCall
    def show_extension(self, ext_alias, **_params):
        """Fetch a list of all exts on server side."""
        return self.get(self.ext_path % ext_alias, params=_params)

    @APIParamsCall
    def list_ports(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.ports_path, params=_params)

    @APIParamsCall
    def show_port(self, port, **_params):
        """
        Fetches information of a certain network
        """
        return self.get(self.port_path % (port), params=_params)

    @APIParamsCall
    def create_port(self, body=None):
        """
        Creates a new port
        """
        return self.post(self.ports_path, body=body)

    @APIParamsCall
    def update_port(self, port, body=None):
        """
        Updates a port
        """
        return self.put(self.port_path % (port), body=body)

    @APIParamsCall
    def delete_port(self, port):
        """
        Deletes the specified port
        """
        return self.delete(self.port_path % (port))

    @APIParamsCall
    def list_networks(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.networks_path, params=_params)

    @APIParamsCall
    def show_network(self, network, **_params):
        """
        Fetches information of a certain network
        """
        return self.get(self.network_path % (network), params=_params)

    @APIParamsCall
    def create_network(self, body=None):
        """
        Creates a new network
        """
        return self.post(self.networks_path, body=body)

    @APIParamsCall
    def update_network(self, network, body=None):
        """
        Updates a network
        """
        return self.put(self.network_path % (network), body=body)

    @APIParamsCall
    def delete_network(self, network):
        """
        Deletes the specified network
        """
        return self.delete(self.network_path % (network))

    @APIParamsCall
    def list_subnets(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        return self.get(self.subnets_path, params=_params)

    @APIParamsCall
    def show_subnet(self, subnet, **_params):
        """
        Fetches information of a certain subnet
        """
        return self.get(self.subnet_path % (subnet), params=_params)

    @APIParamsCall
    def create_subnet(self, body=None):
        """
        Creates a new subnet
        """
        return self.post(self.subnets_path, body=body)

    @APIParamsCall
    def update_subnet(self, subnet, body=None):
        """
        Updates a subnet
        """
        return self.put(self.subnet_path % (subnet), body=body)

    @APIParamsCall
    def delete_subnet(self, subnet):
        """
        Deletes the specified subnet
        """
        return self.delete(self.subnet_path % (subnet))

    @APIParamsCall
    def list_routers(self, **_params):
        """
        Fetches a list of all routers for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.routers_path, params=_params)

    @APIParamsCall
    def show_router(self, router, **_params):
        """
        Fetches information of a certain router
        """
        return self.get(self.router_path % (router), params=_params)

    @APIParamsCall
    def create_router(self, body=None):
        """
        Creates a new router
        """
        return self.post(self.routers_path, body=body)

    @APIParamsCall
    def update_router(self, router, body=None):
        """
        Updates a router
        """
        return self.put(self.router_path % (router), body=body)

    @APIParamsCall
    def delete_router(self, router):
        """
        Deletes the specified router
        """
        return self.delete(self.router_path % (router))

    @APIParamsCall
    def add_interface_router(self, router, body=None):
        """
        Adds an internal network interface to the specified router
        """
        return self.put((self.router_path % router) + "/add_router_interface",
                        body=body)

    @APIParamsCall
    def remove_interface_router(self, router, body=None):
        """
        Removes an internal network interface from the specified router
        """
        return self.put((self.router_path % router) +
                        "/remove_router_interface", body=body)

    @APIParamsCall
    def add_gateway_router(self, router, body=None):
        """
        Adds an external network gateway to the specified router
        """
        return self.put((self.router_path % router),
                        body={'router': {'external_gateway_info': body}})

    @APIParamsCall
    def remove_gateway_router(self, router):
        """
        Removes an external network gateway from the specified router
        """
        return self.put((self.router_path % router),
                        body={'router': {'external_gateway_info': {}}})

    @APIParamsCall
    def list_floatingips(self, **_params):
        """
        Fetches a list of all floatingips for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.floatingips_path, params=_params)

    @APIParamsCall
    def show_floatingip(self, floatingip, **_params):
        """
        Fetches information of a certain floatingip
        """
        return self.get(self.floatingip_path % (floatingip), params=_params)

    @APIParamsCall
    def create_floatingip(self, body=None):
        """
        Creates a new floatingip
        """
        return self.post(self.floatingips_path, body=body)

    @APIParamsCall
    def update_floatingip(self, floatingip, body=None):
        """
        Updates a floatingip
        """
        return self.put(self.floatingip_path % (floatingip), body=body)

    @APIParamsCall
    def delete_floatingip(self, floatingip):
        """
        Deletes the specified floatingip
        """
        return self.delete(self.floatingip_path % (floatingip))

    @APIParamsCall
    def create_security_group(self, body=None):
        """
        Creates a new security group
        """
        return self.post(self.security_groups_path, body=body)

    @APIParamsCall
    def list_security_groups(self, **_params):
        """
        Fetches a list of all security groups for a tenant
        """
        return self.get(self.security_groups_path, params=_params)

    @APIParamsCall
    def show_security_group(self, security_group, **_params):
        """
        Fetches information of a certain security group
        """
        return self.get(self.security_group_path % (security_group),
                        params=_params)

    @APIParamsCall
    def delete_security_group(self, security_group):
        """
        Deletes the specified security group
        """
        return self.delete(self.security_group_path % (security_group))

    @APIParamsCall
    def create_security_group_rule(self, body=None):
        """
        Creates a new security group rule
        """
        return self.post(self.security_group_rules_path, body=body)

    @APIParamsCall
    def delete_security_group_rule(self, security_group_rule):
        """
        Deletes the specified security group rule
        """
        return self.delete(self.security_group_rule_path %
                           (security_group_rule))

    @APIParamsCall
    def list_security_group_rules(self, **_params):
        """
        Fetches a list of all security group rules for a tenant
        """
        return self.get(self.security_group_rules_path, params=_params)

    @APIParamsCall
    def show_security_group_rule(self, security_group_rule, **_params):
        """
        Fetches information of a certain security group rule
        """
        return self.get(self.security_group_rule_path % (security_group_rule),
                        params=_params)

    @APIParamsCall
    def list_vips(self, **_params):
        """
        Fetches a list of all load balancer vips for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.vips_path, params=_params)

    @APIParamsCall
    def show_vip(self, vip, **_params):
        """
        Fetches information of a certain load balancer vip
        """
        return self.get(self.vip_path % (vip), params=_params)

    @APIParamsCall
    def create_vip(self, body=None):
        """
        Creates a new load balancer vip
        """
        return self.post(self.vips_path, body=body)

    @APIParamsCall
    def update_vip(self, vip, body=None):
        """
        Updates a load balancer vip
        """
        return self.put(self.vip_path % (vip), body=body)

    @APIParamsCall
    def delete_vip(self, vip):
        """
        Deletes the specified load balancer vip
        """
        return self.delete(self.vip_path % (vip))

    @APIParamsCall
    def list_pools(self, **_params):
        """
        Fetches a list of all load balancer pools for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.pools_path, params=_params)

    @APIParamsCall
    def show_pool(self, pool, **_params):
        """
        Fetches information of a certain load balancer pool
        """
        return self.get(self.pool_path % (pool), params=_params)

    @APIParamsCall
    def create_pool(self, body=None):
        """
        Creates a new load balancer pool
        """
        return self.post(self.pools_path, body=body)

    @APIParamsCall
    def update_pool(self, pool, body=None):
        """
        Updates a load balancer pool
        """
        return self.put(self.pool_path % (pool), body=body)

    @APIParamsCall
    def delete_pool(self, pool):
        """
        Deletes the specified load balancer pool
        """
        return self.delete(self.pool_path % (pool))

    @APIParamsCall
    def retrieve_pool_stats(self, pool, **_params):
        """
        Retrieves stats for a certain load balancer pool
        """
        return self.get(self.pool_path_stats % (pool), params=_params)

    @APIParamsCall
    def list_members(self, **_params):
        """
        Fetches a list of all load balancer members for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.members_path, params=_params)

    @APIParamsCall
    def show_member(self, member, **_params):
        """
        Fetches information of a certain load balancer member
        """
        return self.get(self.member_path % (member), params=_params)

    @APIParamsCall
    def create_member(self, body=None):
        """
        Creates a new load balancer member
        """
        return self.post(self.members_path, body=body)

    @APIParamsCall
    def update_member(self, member, body=None):
        """
        Updates a load balancer member
        """
        return self.put(self.member_path % (member), body=body)

    @APIParamsCall
    def delete_member(self, member):
        """
        Deletes the specified load balancer member
        """
        return self.delete(self.member_path % (member))

    @APIParamsCall
    def list_health_monitors(self, **_params):
        """
        Fetches a list of all load balancer health monitors for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.health_monitors_path, params=_params)

    @APIParamsCall
    def show_health_monitor(self, health_monitor, **_params):
        """
        Fetches information of a certain load balancer health monitor
        """
        return self.get(self.health_monitor_path % (health_monitor),
                        params=_params)

    @APIParamsCall
    def create_health_monitor(self, body=None):
        """
        Creates a new load balancer health monitor
        """
        return self.post(self.health_monitors_path, body=body)

    @APIParamsCall
    def update_health_monitor(self, health_monitor, body=None):
        """
        Updates a load balancer health monitor
        """
        return self.put(self.health_monitor_path % (health_monitor), body=body)

    @APIParamsCall
    def delete_health_monitor(self, health_monitor):
        """
        Deletes the specified load balancer health monitor
        """
        return self.delete(self.health_monitor_path % (health_monitor))

    @APIParamsCall
    def associate_health_monitor(self, pool, body):
        """
        Associate  specified load balancer health monitor and pool
        """
        return self.post(self.associate_pool_health_monitors_path % (pool),
                         body=body)

    @APIParamsCall
    def disassociate_health_monitor(self, pool, health_monitor):
        """
        Disassociate specified load balancer health monitor and pool
        """
        path = (self.disassociate_pool_health_monitors_path %
                {'pool': pool, 'health_monitor': health_monitor})
        return self.delete(path)

    def __init__(self, **kwargs):
        """ Initialize a new client for the Quantum v2.0 API. """
        super(Client, self).__init__()
        self.httpclient = HTTPClient(**kwargs)
        self.version = '2.0'
        self.format = 'json'
        self.action_prefix = "/v%s" % (self.version)
        self.retries = 0
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body):
        # Create exception with HTTP status code and message
        _logger.debug("Error message: %s", response_body)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = self.deserialize(response_body, status_code)
        except:
            # If unable to deserialized body it is probably not a
            # Quantum error
            des_error_body = {'message': response_body}
        # Raise the appropriate exception
        exception_handler_v20(status_code, des_error_body)

    def do_request(self, method, action, body=None, headers=None, params=None):
        # Add format and tenant_id
        action += ".%s" % self.format
        action = self.action_prefix + action
        if type(params) is dict and params:
            action += '?' + urllib.urlencode(params, doseq=1)
        if body:
            body = self.serialize(body)
        self.httpclient.content_type = self.content_type()
        resp, replybody = self.httpclient.do_request(action, method, body=body)
        status_code = self.get_status_code(resp)
        if status_code in (httplib.OK,
                           httplib.CREATED,
                           httplib.ACCEPTED,
                           httplib.NO_CONTENT):
            return self.deserialize(replybody, status_code)
        else:
            self._handle_fault_response(status_code, replybody)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status

    def serialize(self, data):
        """
        Serializes a dictionary with a single key (which can contain any
        structure) into either xml or json
        """
        if data is None:
            return None
        elif type(data) is dict:
            return serializer.Serializer(
                self.get_attr_metadata()).serialize(data, self.content_type())
        else:
            raise Exception("unable to serialize object of type = '%s'" %
                            type(data))

    def deserialize(self, data, status_code):
        """
        Deserializes an xml or json string into a dictionary
        """
        if status_code == 204:
            return data
        return serializer.Serializer(self.get_attr_metadata()).deserialize(
            data, self.content_type())['body']

    def content_type(self, _format=None):
        """
        Returns the mime-type for either 'xml' or 'json'.  Defaults to the
        currently set format
        """
        _format = _format or self.format
        return "application/%s" % (_format)

    def retry_request(self, method, action, body=None,
                      headers=None, params=None):
        """
        Call do_request with the default retry configuration. Only
        idempotent requests should retry failed connection attempts.

        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        max_attempts = self.retries + 1
        for i in xrange(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params)
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug(_('Retrying connection to quantum service'))
                    time.sleep(self.retry_interval)

        raise exceptions.ConnectionFailed(reason=_("Maximum attempts reached"))

    def delete(self, action, body=None, headers=None, params=None):
        return self.retry_request("DELETE", action, body=body,
                                  headers=headers, params=params)

    def get(self, action, body=None, headers=None, params=None):
        return self.retry_request("GET", action, body=body,
                                  headers=headers, params=params)

    def post(self, action, body=None, headers=None, params=None):
        # Do not retry POST requests to avoid the orphan objects problem.
        return self.do_request("POST", action, body=body,
                               headers=headers, params=params)

    def put(self, action, body=None, headers=None, params=None):
        return self.retry_request("PUT", action, body=body,
                                  headers=headers, params=params)
