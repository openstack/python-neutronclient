# Copyright 2012 OpenStack Foundation.
# Copyright 2015 Hewlett-Packard Development Company, L.P.
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

import inspect
import itertools
import logging
import time

import requests
import six.moves.urllib.parse as urlparse
from six import string_types

from neutronclient._i18n import _
from neutronclient import client
from neutronclient.common import exceptions
from neutronclient.common import extension as client_extension
from neutronclient.common import serializer
from neutronclient.common import utils


_logger = logging.getLogger(__name__)


def exception_handler_v20(status_code, error_content):
    """Exception handler for API v2.0 client.

    This routine generates the appropriate Neutron exception according to
    the contents of the response body.

    :param status_code: HTTP error status code
    :param error_content: deserialized body of error response
    """
    error_dict = None
    request_ids = error_content.request_ids
    if isinstance(error_content, dict):
        error_dict = error_content.get('NeutronError')
    # Find real error type
    client_exc = None
    if error_dict:
        # If Neutron key is found, it will definitely contain
        # a 'message' and 'type' keys?
        try:
            error_type = error_dict['type']
            error_message = error_dict['message']
            if error_dict['detail']:
                error_message += "\n" + error_dict['detail']
            # If corresponding exception is defined, use it.
            client_exc = getattr(exceptions, '%sClient' % error_type, None)
        except Exception:
            error_message = "%s" % error_dict
    else:
        error_message = None
        if isinstance(error_content, dict):
            error_message = error_content.get('message')
        if not error_message:
            # If we end up here the exception was not a neutron error
            error_message = "%s-%s" % (status_code, error_content)

    # If an exception corresponding to the error type is not found,
    # look up per status-code client exception.
    if not client_exc:
        client_exc = exceptions.HTTP_EXCEPTION_MAP.get(status_code)
    # If there is no exception per status-code,
    # Use NeutronClientException as fallback.
    if not client_exc:
        client_exc = exceptions.NeutronClientException

    raise client_exc(message=error_message,
                     status_code=status_code,
                     request_ids=request_ids)


class APIParamsCall(object):
    """A Decorator to support formatting and tenant overriding and filters."""
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


class _RequestIdMixin(object):
    """Wrapper class to expose x-openstack-request-id to the caller."""
    def _request_ids_setup(self):
        self._request_ids = []

    @property
    def request_ids(self):
        return self._request_ids

    def _append_request_ids(self, resp):
        """Add request_ids as an attribute to the object

        :param resp: Response object or list of Response objects
        """
        if isinstance(resp, list):
            # Add list of request_ids if response is of type list.
            for resp_obj in resp:
                self._append_request_id(resp_obj)
        elif resp is not None:
            # Add request_ids if response contains single object.
            self._append_request_id(resp)

    def _append_request_id(self, resp):
        if isinstance(resp, requests.Response):
            # Extract 'x-openstack-request-id' from headers if
            # response is a Response object.
            request_id = resp.headers.get('x-openstack-request-id')
        else:
            # If resp is of type string.
            request_id = resp
        if request_id:
            self._request_ids.append(request_id)


class _DictWithMeta(dict, _RequestIdMixin):
    def __init__(self, values, resp):
        super(_DictWithMeta, self).__init__(values)
        self._request_ids_setup()
        self._append_request_ids(resp)


class _TupleWithMeta(tuple, _RequestIdMixin):
    def __new__(cls, values, resp):
        return super(_TupleWithMeta, cls).__new__(cls, values)

    def __init__(self, values, resp):
        self._request_ids_setup()
        self._append_request_ids(resp)


class _StrWithMeta(str, _RequestIdMixin):
    def __new__(cls, value, resp):
        return super(_StrWithMeta, cls).__new__(cls, value)

    def __init__(self, values, resp):
        self._request_ids_setup()
        self._append_request_ids(resp)


class _GeneratorWithMeta(_RequestIdMixin):
    def __init__(self, paginate_func, collection, path, **params):
        self.paginate_func = paginate_func
        self.collection = collection
        self.path = path
        self.params = params
        self.generator = None
        self._request_ids_setup()

    def _paginate(self):
        for r in self.paginate_func(
                self.collection, self.path, **self.params):
            yield r, r.request_ids

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if not self.generator:
            self.generator = self._paginate()

        try:
            obj, req_id = next(self.generator)
            self._append_request_ids(req_id)
        except StopIteration:
            raise StopIteration()

        return obj


class ClientBase(object):
    """Client for the OpenStack Neutron v2.0 API.

    :param string username: Username for authentication. (optional)
    :param string user_id: User ID for authentication. (optional)
    :param string password: Password for authentication. (optional)
    :param string token: Token for authentication. (optional)
    :param string tenant_name: Tenant name. (optional)
    :param string tenant_id: Tenant id. (optional)
    :param string auth_strategy: 'keystone' by default, 'noauth' for no
                                 authentication against keystone. (optional)
    :param string auth_url: Keystone service endpoint for authorization.
    :param string service_type: Network service type to pull from the
                                keystone catalog (e.g. 'network') (optional)
    :param string endpoint_type: Network service endpoint type to pull from the
                                 keystone catalog (e.g. 'publicURL',
                                 'internalURL', or 'adminURL') (optional)
    :param string region_name: Name of a region to select when choosing an
                               endpoint from the service catalog.
    :param string endpoint_url: A user-supplied endpoint URL for the neutron
                            service.  Lazy-authentication is possible for API
                            service calls if endpoint is set at
                            instantiation.(optional)
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    :param bool insecure: SSL certificate validation. (optional)
    :param bool log_credentials: Allow for logging of passwords or not.
                                 Defaults to False. (optional)
    :param string ca_cert: SSL CA bundle file to use. (optional)
    :param integer retries: How many times idempotent (GET, PUT, DELETE)
                            requests to Neutron server should be retried if
                            they fail (default: 0).
    :param bool raise_errors: If True then exceptions caused by connection
                              failure are propagated to the caller.
                              (default: True)
    :param session: Keystone client auth session to use. (optional)
    :param auth: Keystone auth plugin to use. (optional)

    Example::

        from neutronclient.v2_0 import client
        neutron = client.Client(username=USER,
                                password=PASS,
                                tenant_name=TENANT_NAME,
                                auth_url=KEYSTONE_URL)

        nets = neutron.list_networks()
        ...
    """

    # API has no way to report plurals, so we have to hard code them
    # This variable should be overridden by a child class.
    EXTED_PLURALS = {}

    def __init__(self, **kwargs):
        """Initialize a new client for the Neutron v2.0 API."""
        super(ClientBase, self).__init__()
        self.retries = kwargs.pop('retries', 0)
        self.raise_errors = kwargs.pop('raise_errors', True)
        self.httpclient = client.construct_http_client(**kwargs)
        self.version = '2.0'
        self.format = 'json'
        self.action_prefix = "/v%s" % (self.version)
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body, resp):
        # Create exception with HTTP status code and message
        _logger.debug("Error message: %s", response_body)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = self.deserialize(response_body, status_code)
        except Exception:
            # If unable to deserialized body it is probably not a
            # Neutron error
            des_error_body = {'message': response_body}
        error_body = self._convert_into_with_meta(des_error_body, resp)
        # Raise the appropriate exception
        exception_handler_v20(status_code, error_body)

    def do_request(self, method, action, body=None, headers=None, params=None):
        # Add format and tenant_id
        action += ".%s" % self.format
        action = self.action_prefix + action
        if isinstance(params, dict) and params:
            params = utils.safe_encode_dict(params)
            action += '?' + urlparse.urlencode(params, doseq=1)

        if body:
            body = self.serialize(body)

        resp, replybody = self.httpclient.do_request(action, method, body=body)

        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            data = self.deserialize(replybody, status_code)
            return self._convert_into_with_meta(data, resp)
        else:
            if not replybody:
                replybody = resp.reason
            self._handle_fault_response(status_code, replybody, resp)

    def get_auth_info(self):
        return self.httpclient.get_auth_info()

    def serialize(self, data):
        """Serializes a dictionary into JSON.

        A dictionary with a single key can be passed and it can contain any
        structure.
        """
        if data is None:
            return None
        elif isinstance(data, dict):
            return serializer.Serializer().serialize(data)
        else:
            raise Exception(_("Unable to serialize object of type = '%s'") %
                            type(data))

    def deserialize(self, data, status_code):
        """Deserializes a JSON string into a dictionary."""
        if status_code == 204:
            return data
        return serializer.Serializer().deserialize(
            data)['body']

    def retry_request(self, method, action, body=None,
                      headers=None, params=None):
        """Call do_request with the default retry configuration.

        Only idempotent requests should retry failed connection attempts.
        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        max_attempts = self.retries + 1
        for i in range(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params)
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug('Retrying connection to Neutron service')
                    time.sleep(self.retry_interval)
                elif self.raise_errors:
                    raise

        if self.retries:
            msg = (_("Failed to connect to Neutron server after %d attempts")
                   % max_attempts)
        else:
            msg = _("Failed to connect Neutron server")

        raise exceptions.ConnectionFailed(reason=msg)

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

    def list(self, collection, path, retrieve_all=True, **params):
        if retrieve_all:
            res = []
            request_ids = []
            for r in self._pagination(collection, path, **params):
                res.extend(r[collection])
                request_ids.extend(r.request_ids)
            return _DictWithMeta({collection: res}, request_ids)
        else:
            return _GeneratorWithMeta(self._pagination, collection,
                                      path, **params)

    def _pagination(self, collection, path, **params):
        if params.get('page_reverse', False):
            linkrel = 'previous'
        else:
            linkrel = 'next'
        next = True
        while next:
            res = self.get(path, params=params)
            yield res
            next = False
            try:
                for link in res['%s_links' % collection]:
                    if link['rel'] == linkrel:
                        query_str = urlparse.urlparse(link['href']).query
                        params = urlparse.parse_qs(query_str)
                        next = True
                        break
            except KeyError:
                break

    def _convert_into_with_meta(self, item, resp):
        if item:
            if isinstance(item, dict):
                return _DictWithMeta(item, resp)
            elif isinstance(item, string_types):
                return _StrWithMeta(item, resp)
        else:
            return _TupleWithMeta((), resp)


class Client(ClientBase):

    networks_path = "/networks"
    network_path = "/networks/%s"
    ports_path = "/ports"
    port_path = "/ports/%s"
    subnets_path = "/subnets"
    subnet_path = "/subnets/%s"
    subnetpools_path = "/subnetpools"
    subnetpool_path = "/subnetpools/%s"
    address_scopes_path = "/address-scopes"
    address_scope_path = "/address-scopes/%s"
    quotas_path = "/quotas"
    quota_path = "/quotas/%s"
    extensions_path = "/extensions"
    extension_path = "/extensions/%s"
    routers_path = "/routers"
    router_path = "/routers/%s"
    floatingips_path = "/floatingips"
    floatingip_path = "/floatingips/%s"
    security_groups_path = "/security-groups"
    security_group_path = "/security-groups/%s"
    security_group_rules_path = "/security-group-rules"
    security_group_rule_path = "/security-group-rules/%s"
    endpoint_groups_path = "/vpn/endpoint-groups"
    endpoint_group_path = "/vpn/endpoint-groups/%s"
    vpnservices_path = "/vpn/vpnservices"
    vpnservice_path = "/vpn/vpnservices/%s"
    ipsecpolicies_path = "/vpn/ipsecpolicies"
    ipsecpolicy_path = "/vpn/ipsecpolicies/%s"
    ikepolicies_path = "/vpn/ikepolicies"
    ikepolicy_path = "/vpn/ikepolicies/%s"
    ipsec_site_connections_path = "/vpn/ipsec-site-connections"
    ipsec_site_connection_path = "/vpn/ipsec-site-connections/%s"

    lbaas_loadbalancers_path = "/lbaas/loadbalancers"
    lbaas_loadbalancer_path = "/lbaas/loadbalancers/%s"
    lbaas_loadbalancer_path_stats = "/lbaas/loadbalancers/%s/stats"
    lbaas_loadbalancer_path_status = "/lbaas/loadbalancers/%s/statuses"
    lbaas_listeners_path = "/lbaas/listeners"
    lbaas_listener_path = "/lbaas/listeners/%s"
    lbaas_l7policies_path = "/lbaas/l7policies"
    lbaas_l7policy_path = lbaas_l7policies_path + "/%s"
    lbaas_l7rules_path = lbaas_l7policy_path + "/rules"
    lbaas_l7rule_path = lbaas_l7rules_path + "/%s"
    lbaas_pools_path = "/lbaas/pools"
    lbaas_pool_path = "/lbaas/pools/%s"
    lbaas_healthmonitors_path = "/lbaas/healthmonitors"
    lbaas_healthmonitor_path = "/lbaas/healthmonitors/%s"
    lbaas_members_path = lbaas_pool_path + "/members"
    lbaas_member_path = lbaas_pool_path + "/members/%s"

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
    qos_queues_path = "/qos-queues"
    qos_queue_path = "/qos-queues/%s"
    agents_path = "/agents"
    agent_path = "/agents/%s"
    network_gateways_path = "/network-gateways"
    network_gateway_path = "/network-gateways/%s"
    gateway_devices_path = "/gateway-devices"
    gateway_device_path = "/gateway-devices/%s"
    service_providers_path = "/service-providers"
    metering_labels_path = "/metering/metering-labels"
    metering_label_path = "/metering/metering-labels/%s"
    metering_label_rules_path = "/metering/metering-label-rules"
    metering_label_rule_path = "/metering/metering-label-rules/%s"

    DHCP_NETS = '/dhcp-networks'
    DHCP_AGENTS = '/dhcp-agents'
    L3_ROUTERS = '/l3-routers'
    L3_AGENTS = '/l3-agents'
    LOADBALANCER_POOLS = '/loadbalancer-pools'
    LOADBALANCER_AGENT = '/loadbalancer-agent'
    AGENT_LOADBALANCERS = '/agent-loadbalancers'
    LOADBALANCER_HOSTING_AGENT = '/loadbalancer-hosting-agent'
    firewall_rules_path = "/fw/firewall_rules"
    firewall_rule_path = "/fw/firewall_rules/%s"
    firewall_policies_path = "/fw/firewall_policies"
    firewall_policy_path = "/fw/firewall_policies/%s"
    firewall_policy_insert_path = "/fw/firewall_policies/%s/insert_rule"
    firewall_policy_remove_path = "/fw/firewall_policies/%s/remove_rule"
    firewalls_path = "/fw/firewalls"
    firewall_path = "/fw/firewalls/%s"
    rbac_policies_path = "/rbac-policies"
    rbac_policy_path = "/rbac-policies/%s"
    qos_policies_path = "/qos/policies"
    qos_policy_path = "/qos/policies/%s"
    qos_bandwidth_limit_rules_path = "/qos/policies/%s/bandwidth_limit_rules"
    qos_bandwidth_limit_rule_path = "/qos/policies/%s/bandwidth_limit_rules/%s"
    qos_rule_types_path = "/qos/rule-types"
    qos_rule_type_path = "/qos/rule-types/%s"
    flavors_path = "/flavors"
    flavor_path = "/flavors/%s"
    service_profiles_path = "/service_profiles"
    service_profile_path = "/service_profiles/%s"
    flavor_profile_bindings_path = flavor_path + service_profiles_path
    flavor_profile_binding_path = flavor_path + service_profile_path
    availability_zones_path = "/availability_zones"
    auto_allocated_topology_path = "/auto-allocated-topology/%s"
    BGP_DRINSTANCES = "/bgp-drinstances"
    BGP_DRINSTANCE = "/bgp-drinstance/%s"
    BGP_DRAGENTS = "/bgp-dragents"
    BGP_DRAGENT = "/bgp-dragents/%s"
    bgp_speakers_path = "/bgp-speakers"
    bgp_speaker_path = "/bgp-speakers/%s"
    bgp_peers_path = "/bgp-peers"
    bgp_peer_path = "/bgp-peers/%s"
    network_ip_availabilities_path = '/network-ip-availabilities'
    network_ip_availability_path = '/network-ip-availabilities/%s'
    tags_path = "/%s/%s/tags"
    tag_path = "/%s/%s/tags/%s"

    # API has no way to report plurals, so we have to hard code them
    EXTED_PLURALS = {'routers': 'router',
                     'floatingips': 'floatingip',
                     'service_types': 'service_type',
                     'service_definitions': 'service_definition',
                     'security_groups': 'security_group',
                     'security_group_rules': 'security_group_rule',
                     'ipsecpolicies': 'ipsecpolicy',
                     'ikepolicies': 'ikepolicy',
                     'ipsec_site_connections': 'ipsec_site_connection',
                     'vpnservices': 'vpnservice',
                     'endpoint_groups': 'endpoint_group',
                     'vips': 'vip',
                     'pools': 'pool',
                     'members': 'member',
                     'health_monitors': 'health_monitor',
                     'quotas': 'quota',
                     'service_providers': 'service_provider',
                     'firewall_rules': 'firewall_rule',
                     'firewall_policies': 'firewall_policy',
                     'firewalls': 'firewall',
                     'metering_labels': 'metering_label',
                     'metering_label_rules': 'metering_label_rule',
                     'loadbalancers': 'loadbalancer',
                     'listeners': 'listener',
                     'l7rules': 'l7rule',
                     'l7policies': 'l7policy',
                     'lbaas_l7policies': 'lbaas_l7policy',
                     'lbaas_pools': 'lbaas_pool',
                     'lbaas_healthmonitors': 'lbaas_healthmonitor',
                     'lbaas_members': 'lbaas_member',
                     'healthmonitors': 'healthmonitor',
                     'rbac_policies': 'rbac_policy',
                     'address_scopes': 'address_scope',
                     'qos_policies': 'qos_policy',
                     'policies': 'policy',
                     'bandwidth_limit_rules': 'bandwidth_limit_rule',
                     'rules': 'rule',
                     'rule_types': 'rule_type',
                     'flavors': 'flavor',
                     'bgp_speakers': 'bgp_speaker',
                     'bgp_peers': 'bgp_peer',
                     'network_ip_availabilities': 'network_ip_availability',
                     }

    @APIParamsCall
    def list_ext(self, collection, path, retrieve_all, **_params):
        """Client extension hook for list."""
        return self.list(collection, path, retrieve_all, **_params)

    @APIParamsCall
    def show_ext(self, path, id, **_params):
        """Client extension hook for show."""
        return self.get(path % id, params=_params)

    @APIParamsCall
    def create_ext(self, path, body=None):
        """Client extension hook for create."""
        return self.post(path, body=body)

    @APIParamsCall
    def update_ext(self, path, id, body=None):
        """Client extension hook for update."""
        return self.put(path % id, body=body)

    @APIParamsCall
    def delete_ext(self, path, id):
        """Client extension hook for delete."""
        return self.delete(path % id)

    @APIParamsCall
    def get_quotas_tenant(self, **_params):
        """Fetch tenant info for following quota operation."""
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
        """Fetch a list of all extensions on server side."""
        return self.get(self.extensions_path, params=_params)

    @APIParamsCall
    def show_extension(self, ext_alias, **_params):
        """Fetches information of a certain extension."""
        return self.get(self.extension_path % ext_alias, params=_params)

    @APIParamsCall
    def list_ports(self, retrieve_all=True, **_params):
        """Fetches a list of all ports for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('ports', self.ports_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_port(self, port, **_params):
        """Fetches information of a certain port."""
        return self.get(self.port_path % (port), params=_params)

    @APIParamsCall
    def create_port(self, body=None):
        """Creates a new port."""
        return self.post(self.ports_path, body=body)

    @APIParamsCall
    def update_port(self, port, body=None):
        """Updates a port."""
        return self.put(self.port_path % (port), body=body)

    @APIParamsCall
    def delete_port(self, port):
        """Deletes the specified port."""
        return self.delete(self.port_path % (port))

    @APIParamsCall
    def list_networks(self, retrieve_all=True, **_params):
        """Fetches a list of all networks for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('networks', self.networks_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_network(self, network, **_params):
        """Fetches information of a certain network."""
        return self.get(self.network_path % (network), params=_params)

    @APIParamsCall
    def create_network(self, body=None):
        """Creates a new network."""
        return self.post(self.networks_path, body=body)

    @APIParamsCall
    def update_network(self, network, body=None):
        """Updates a network."""
        return self.put(self.network_path % (network), body=body)

    @APIParamsCall
    def delete_network(self, network):
        """Deletes the specified network."""
        return self.delete(self.network_path % (network))

    @APIParamsCall
    def list_subnets(self, retrieve_all=True, **_params):
        """Fetches a list of all subnets for a tenant."""
        return self.list('subnets', self.subnets_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_subnet(self, subnet, **_params):
        """Fetches information of a certain subnet."""
        return self.get(self.subnet_path % (subnet), params=_params)

    @APIParamsCall
    def create_subnet(self, body=None):
        """Creates a new subnet."""
        return self.post(self.subnets_path, body=body)

    @APIParamsCall
    def update_subnet(self, subnet, body=None):
        """Updates a subnet."""
        return self.put(self.subnet_path % (subnet), body=body)

    @APIParamsCall
    def delete_subnet(self, subnet):
        """Deletes the specified subnet."""
        return self.delete(self.subnet_path % (subnet))

    @APIParamsCall
    def list_subnetpools(self, retrieve_all=True, **_params):
        """Fetches a list of all subnetpools for a tenant."""
        return self.list('subnetpools', self.subnetpools_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_subnetpool(self, subnetpool, **_params):
        """Fetches information of a certain subnetpool."""
        return self.get(self.subnetpool_path % (subnetpool), params=_params)

    @APIParamsCall
    def create_subnetpool(self, body=None):
        """Creates a new subnetpool."""
        return self.post(self.subnetpools_path, body=body)

    @APIParamsCall
    def update_subnetpool(self, subnetpool, body=None):
        """Updates a subnetpool."""
        return self.put(self.subnetpool_path % (subnetpool), body=body)

    @APIParamsCall
    def delete_subnetpool(self, subnetpool):
        """Deletes the specified subnetpool."""
        return self.delete(self.subnetpool_path % (subnetpool))

    @APIParamsCall
    def list_routers(self, retrieve_all=True, **_params):
        """Fetches a list of all routers for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('routers', self.routers_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_router(self, router, **_params):
        """Fetches information of a certain router."""
        return self.get(self.router_path % (router), params=_params)

    @APIParamsCall
    def create_router(self, body=None):
        """Creates a new router."""
        return self.post(self.routers_path, body=body)

    @APIParamsCall
    def update_router(self, router, body=None):
        """Updates a router."""
        return self.put(self.router_path % (router), body=body)

    @APIParamsCall
    def delete_router(self, router):
        """Deletes the specified router."""
        return self.delete(self.router_path % (router))

    @APIParamsCall
    def list_address_scopes(self, retrieve_all=True, **_params):
        """Fetches a list of all address scopes for a tenant."""
        return self.list('address_scopes', self.address_scopes_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_address_scope(self, address_scope, **_params):
        """Fetches information of a certain address scope."""
        return self.get(self.address_scope_path % (address_scope),
                        params=_params)

    @APIParamsCall
    def create_address_scope(self, body=None):
        """Creates a new address scope."""
        return self.post(self.address_scopes_path, body=body)

    @APIParamsCall
    def update_address_scope(self, address_scope, body=None):
        """Updates a address scope."""
        return self.put(self.address_scope_path % (address_scope), body=body)

    @APIParamsCall
    def delete_address_scope(self, address_scope):
        """Deletes the specified address scope."""
        return self.delete(self.address_scope_path % (address_scope))

    @APIParamsCall
    def add_interface_router(self, router, body=None):
        """Adds an internal network interface to the specified router."""
        return self.put((self.router_path % router) + "/add_router_interface",
                        body=body)

    @APIParamsCall
    def remove_interface_router(self, router, body=None):
        """Removes an internal network interface from the specified router."""
        return self.put((self.router_path % router) +
                        "/remove_router_interface", body=body)

    @APIParamsCall
    def add_gateway_router(self, router, body=None):
        """Adds an external network gateway to the specified router."""
        return self.put((self.router_path % router),
                        body={'router': {'external_gateway_info': body}})

    @APIParamsCall
    def remove_gateway_router(self, router):
        """Removes an external network gateway from the specified router."""
        return self.put((self.router_path % router),
                        body={'router': {'external_gateway_info': {}}})

    @APIParamsCall
    def list_floatingips(self, retrieve_all=True, **_params):
        """Fetches a list of all floatingips for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('floatingips', self.floatingips_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_floatingip(self, floatingip, **_params):
        """Fetches information of a certain floatingip."""
        return self.get(self.floatingip_path % (floatingip), params=_params)

    @APIParamsCall
    def create_floatingip(self, body=None):
        """Creates a new floatingip."""
        return self.post(self.floatingips_path, body=body)

    @APIParamsCall
    def update_floatingip(self, floatingip, body=None):
        """Updates a floatingip."""
        return self.put(self.floatingip_path % (floatingip), body=body)

    @APIParamsCall
    def delete_floatingip(self, floatingip):
        """Deletes the specified floatingip."""
        return self.delete(self.floatingip_path % (floatingip))

    @APIParamsCall
    def create_security_group(self, body=None):
        """Creates a new security group."""
        return self.post(self.security_groups_path, body=body)

    @APIParamsCall
    def update_security_group(self, security_group, body=None):
        """Updates a security group."""
        return self.put(self.security_group_path %
                        security_group, body=body)

    @APIParamsCall
    def list_security_groups(self, retrieve_all=True, **_params):
        """Fetches a list of all security groups for a tenant."""
        return self.list('security_groups', self.security_groups_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_security_group(self, security_group, **_params):
        """Fetches information of a certain security group."""
        return self.get(self.security_group_path % (security_group),
                        params=_params)

    @APIParamsCall
    def delete_security_group(self, security_group):
        """Deletes the specified security group."""
        return self.delete(self.security_group_path % (security_group))

    @APIParamsCall
    def create_security_group_rule(self, body=None):
        """Creates a new security group rule."""
        return self.post(self.security_group_rules_path, body=body)

    @APIParamsCall
    def delete_security_group_rule(self, security_group_rule):
        """Deletes the specified security group rule."""
        return self.delete(self.security_group_rule_path %
                           (security_group_rule))

    @APIParamsCall
    def list_security_group_rules(self, retrieve_all=True, **_params):
        """Fetches a list of all security group rules for a tenant."""
        return self.list('security_group_rules',
                         self.security_group_rules_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_security_group_rule(self, security_group_rule, **_params):
        """Fetches information of a certain security group rule."""
        return self.get(self.security_group_rule_path % (security_group_rule),
                        params=_params)

    @APIParamsCall
    def list_endpoint_groups(self, retrieve_all=True, **_params):
        """Fetches a list of all VPN endpoint groups for a tenant."""
        return self.list('endpoint_groups', self.endpoint_groups_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_endpoint_group(self, endpointgroup, **_params):
        """Fetches information for a specific VPN endpoint group."""
        return self.get(self.endpoint_group_path % endpointgroup,
                        params=_params)

    @APIParamsCall
    def create_endpoint_group(self, body=None):
        """Creates a new VPN endpoint group."""
        return self.post(self.endpoint_groups_path, body=body)

    @APIParamsCall
    def update_endpoint_group(self, endpoint_group, body=None):
        """Updates a VPN endpoint group."""
        return self.put(self.endpoint_group_path % endpoint_group, body=body)

    @APIParamsCall
    def delete_endpoint_group(self, endpoint_group):
        """Deletes the specified VPN endpoint group."""
        return self.delete(self.endpoint_group_path % endpoint_group)

    @APIParamsCall
    def list_vpnservices(self, retrieve_all=True, **_params):
        """Fetches a list of all configured VPN services for a tenant."""
        return self.list('vpnservices', self.vpnservices_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_vpnservice(self, vpnservice, **_params):
        """Fetches information of a specific VPN service."""
        return self.get(self.vpnservice_path % (vpnservice), params=_params)

    @APIParamsCall
    def create_vpnservice(self, body=None):
        """Creates a new VPN service."""
        return self.post(self.vpnservices_path, body=body)

    @APIParamsCall
    def update_vpnservice(self, vpnservice, body=None):
        """Updates a VPN service."""
        return self.put(self.vpnservice_path % (vpnservice), body=body)

    @APIParamsCall
    def delete_vpnservice(self, vpnservice):
        """Deletes the specified VPN service."""
        return self.delete(self.vpnservice_path % (vpnservice))

    @APIParamsCall
    def list_ipsec_site_connections(self, retrieve_all=True, **_params):
        """Fetches all configured IPsecSiteConnections for a tenant."""
        return self.list('ipsec_site_connections',
                         self.ipsec_site_connections_path,
                         retrieve_all,
                         **_params)

    @APIParamsCall
    def show_ipsec_site_connection(self, ipsecsite_conn, **_params):
        """Fetches information of a specific IPsecSiteConnection."""
        return self.get(
            self.ipsec_site_connection_path % (ipsecsite_conn), params=_params
        )

    @APIParamsCall
    def create_ipsec_site_connection(self, body=None):
        """Creates a new IPsecSiteConnection."""
        return self.post(self.ipsec_site_connections_path, body=body)

    @APIParamsCall
    def update_ipsec_site_connection(self, ipsecsite_conn, body=None):
        """Updates an IPsecSiteConnection."""
        return self.put(
            self.ipsec_site_connection_path % (ipsecsite_conn), body=body
        )

    @APIParamsCall
    def delete_ipsec_site_connection(self, ipsecsite_conn):
        """Deletes the specified IPsecSiteConnection."""
        return self.delete(self.ipsec_site_connection_path % (ipsecsite_conn))

    @APIParamsCall
    def list_ikepolicies(self, retrieve_all=True, **_params):
        """Fetches a list of all configured IKEPolicies for a tenant."""
        return self.list('ikepolicies', self.ikepolicies_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_ikepolicy(self, ikepolicy, **_params):
        """Fetches information of a specific IKEPolicy."""
        return self.get(self.ikepolicy_path % (ikepolicy), params=_params)

    @APIParamsCall
    def create_ikepolicy(self, body=None):
        """Creates a new IKEPolicy."""
        return self.post(self.ikepolicies_path, body=body)

    @APIParamsCall
    def update_ikepolicy(self, ikepolicy, body=None):
        """Updates an IKEPolicy."""
        return self.put(self.ikepolicy_path % (ikepolicy), body=body)

    @APIParamsCall
    def delete_ikepolicy(self, ikepolicy):
        """Deletes the specified IKEPolicy."""
        return self.delete(self.ikepolicy_path % (ikepolicy))

    @APIParamsCall
    def list_ipsecpolicies(self, retrieve_all=True, **_params):
        """Fetches a list of all configured IPsecPolicies for a tenant."""
        return self.list('ipsecpolicies',
                         self.ipsecpolicies_path,
                         retrieve_all,
                         **_params)

    @APIParamsCall
    def show_ipsecpolicy(self, ipsecpolicy, **_params):
        """Fetches information of a specific IPsecPolicy."""
        return self.get(self.ipsecpolicy_path % (ipsecpolicy), params=_params)

    @APIParamsCall
    def create_ipsecpolicy(self, body=None):
        """Creates a new IPsecPolicy."""
        return self.post(self.ipsecpolicies_path, body=body)

    @APIParamsCall
    def update_ipsecpolicy(self, ipsecpolicy, body=None):
        """Updates an IPsecPolicy."""
        return self.put(self.ipsecpolicy_path % (ipsecpolicy), body=body)

    @APIParamsCall
    def delete_ipsecpolicy(self, ipsecpolicy):
        """Deletes the specified IPsecPolicy."""
        return self.delete(self.ipsecpolicy_path % (ipsecpolicy))

    @APIParamsCall
    def list_loadbalancers(self, retrieve_all=True, **_params):
        """Fetches a list of all loadbalancers for a tenant."""
        return self.list('loadbalancers', self.lbaas_loadbalancers_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_loadbalancer(self, lbaas_loadbalancer, **_params):
        """Fetches information for a load balancer."""
        return self.get(self.lbaas_loadbalancer_path % (lbaas_loadbalancer),
                        params=_params)

    @APIParamsCall
    def create_loadbalancer(self, body=None):
        """Creates a new load balancer."""
        return self.post(self.lbaas_loadbalancers_path, body=body)

    @APIParamsCall
    def update_loadbalancer(self, lbaas_loadbalancer, body=None):
        """Updates a load balancer."""
        return self.put(self.lbaas_loadbalancer_path % (lbaas_loadbalancer),
                        body=body)

    @APIParamsCall
    def delete_loadbalancer(self, lbaas_loadbalancer):
        """Deletes the specified load balancer."""
        return self.delete(self.lbaas_loadbalancer_path %
                           (lbaas_loadbalancer))

    @APIParamsCall
    def retrieve_loadbalancer_stats(self, loadbalancer, **_params):
        """Retrieves stats for a certain load balancer."""
        return self.get(self.lbaas_loadbalancer_path_stats % (loadbalancer),
                        params=_params)

    @APIParamsCall
    def retrieve_loadbalancer_status(self, loadbalancer, **_params):
        """Retrieves status for a certain load balancer."""
        return self.get(self.lbaas_loadbalancer_path_status % (loadbalancer),
                        params=_params)

    @APIParamsCall
    def list_listeners(self, retrieve_all=True, **_params):
        """Fetches a list of all lbaas_listeners for a tenant."""
        return self.list('listeners', self.lbaas_listeners_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_listener(self, lbaas_listener, **_params):
        """Fetches information for a lbaas_listener."""
        return self.get(self.lbaas_listener_path % (lbaas_listener),
                        params=_params)

    @APIParamsCall
    def create_listener(self, body=None):
        """Creates a new lbaas_listener."""
        return self.post(self.lbaas_listeners_path, body=body)

    @APIParamsCall
    def update_listener(self, lbaas_listener, body=None):
        """Updates a lbaas_listener."""
        return self.put(self.lbaas_listener_path % (lbaas_listener),
                        body=body)

    @APIParamsCall
    def delete_listener(self, lbaas_listener):
        """Deletes the specified lbaas_listener."""
        return self.delete(self.lbaas_listener_path % (lbaas_listener))

    @APIParamsCall
    def list_lbaas_l7policies(self, retrieve_all=True, **_params):
        """Fetches a list of all L7 policies for a listener."""
        return self.list('l7policies', self.lbaas_l7policies_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_lbaas_l7policy(self, l7policy, **_params):
        """Fetches information of a certain listener's L7 policy."""
        return self.get(self.lbaas_l7policy_path % l7policy,
                        params=_params)

    @APIParamsCall
    def create_lbaas_l7policy(self, body=None):
        """Creates L7 policy for a certain listener."""
        return self.post(self.lbaas_l7policies_path, body=body)

    @APIParamsCall
    def update_lbaas_l7policy(self, l7policy, body=None):
        """Updates L7 policy."""
        return self.put(self.lbaas_l7policy_path % l7policy,
                        body=body)

    @APIParamsCall
    def delete_lbaas_l7policy(self, l7policy):
        """Deletes the specified L7 policy."""
        return self.delete(self.lbaas_l7policy_path % l7policy)

    @APIParamsCall
    def list_lbaas_l7rules(self, l7policy, retrieve_all=True, **_params):
        """Fetches a list of all rules for L7 policy."""
        return self.list('rules', self.lbaas_l7rules_path % l7policy,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_lbaas_l7rule(self, l7rule, l7policy, **_params):
        """Fetches information of a certain L7 policy's rule."""
        return self.get(self.lbaas_l7rule_path % (l7policy, l7rule),
                        params=_params)

    @APIParamsCall
    def create_lbaas_l7rule(self, l7policy, body=None):
        """Creates rule for a certain L7 policy."""
        return self.post(self.lbaas_l7rules_path % l7policy, body=body)

    @APIParamsCall
    def update_lbaas_l7rule(self, l7rule, l7policy, body=None):
        """Updates L7 rule."""
        return self.put(self.lbaas_l7rule_path % (l7policy, l7rule),
                        body=body)

    @APIParamsCall
    def delete_lbaas_l7rule(self, l7rule, l7policy):
        """Deletes the specified L7 rule."""
        return self.delete(self.lbaas_l7rule_path % (l7policy, l7rule))

    @APIParamsCall
    def list_lbaas_pools(self, retrieve_all=True, **_params):
        """Fetches a list of all lbaas_pools for a tenant."""
        return self.list('pools', self.lbaas_pools_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_lbaas_pool(self, lbaas_pool, **_params):
        """Fetches information for a lbaas_pool."""
        return self.get(self.lbaas_pool_path % (lbaas_pool),
                        params=_params)

    @APIParamsCall
    def create_lbaas_pool(self, body=None):
        """Creates a new lbaas_pool."""
        return self.post(self.lbaas_pools_path, body=body)

    @APIParamsCall
    def update_lbaas_pool(self, lbaas_pool, body=None):
        """Updates a lbaas_pool."""
        return self.put(self.lbaas_pool_path % (lbaas_pool),
                        body=body)

    @APIParamsCall
    def delete_lbaas_pool(self, lbaas_pool):
        """Deletes the specified lbaas_pool."""
        return self.delete(self.lbaas_pool_path % (lbaas_pool))

    @APIParamsCall
    def list_lbaas_healthmonitors(self, retrieve_all=True, **_params):
        """Fetches a list of all lbaas_healthmonitors for a tenant."""
        return self.list('healthmonitors', self.lbaas_healthmonitors_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_lbaas_healthmonitor(self, lbaas_healthmonitor, **_params):
        """Fetches information for a lbaas_healthmonitor."""
        return self.get(self.lbaas_healthmonitor_path % (lbaas_healthmonitor),
                        params=_params)

    @APIParamsCall
    def create_lbaas_healthmonitor(self, body=None):
        """Creates a new lbaas_healthmonitor."""
        return self.post(self.lbaas_healthmonitors_path, body=body)

    @APIParamsCall
    def update_lbaas_healthmonitor(self, lbaas_healthmonitor, body=None):
        """Updates a lbaas_healthmonitor."""
        return self.put(self.lbaas_healthmonitor_path % (lbaas_healthmonitor),
                        body=body)

    @APIParamsCall
    def delete_lbaas_healthmonitor(self, lbaas_healthmonitor):
        """Deletes the specified lbaas_healthmonitor."""
        return self.delete(self.lbaas_healthmonitor_path %
                           (lbaas_healthmonitor))

    @APIParamsCall
    def list_lbaas_loadbalancers(self, retrieve_all=True, **_params):
        """Fetches a list of all lbaas_loadbalancers for a tenant."""
        return self.list('loadbalancers', self.lbaas_loadbalancers_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def list_lbaas_members(self, lbaas_pool, retrieve_all=True, **_params):
        """Fetches a list of all lbaas_members for a tenant."""
        return self.list('members', self.lbaas_members_path % lbaas_pool,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_lbaas_member(self, lbaas_member, lbaas_pool, **_params):
        """Fetches information of a certain lbaas_member."""
        return self.get(self.lbaas_member_path % (lbaas_pool, lbaas_member),
                        params=_params)

    @APIParamsCall
    def create_lbaas_member(self, lbaas_pool, body=None):
        """Creates an lbaas_member."""
        return self.post(self.lbaas_members_path % lbaas_pool, body=body)

    @APIParamsCall
    def update_lbaas_member(self, lbaas_member, lbaas_pool, body=None):
        """Updates a lbaas_healthmonitor."""
        return self.put(self.lbaas_member_path % (lbaas_pool, lbaas_member),
                        body=body)

    @APIParamsCall
    def delete_lbaas_member(self, lbaas_member, lbaas_pool):
        """Deletes the specified lbaas_member."""
        return self.delete(self.lbaas_member_path % (lbaas_pool, lbaas_member))

    @APIParamsCall
    def list_vips(self, retrieve_all=True, **_params):
        """Fetches a list of all load balancer vips for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('vips', self.vips_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_vip(self, vip, **_params):
        """Fetches information of a certain load balancer vip."""
        return self.get(self.vip_path % (vip), params=_params)

    @APIParamsCall
    def create_vip(self, body=None):
        """Creates a new load balancer vip."""
        return self.post(self.vips_path, body=body)

    @APIParamsCall
    def update_vip(self, vip, body=None):
        """Updates a load balancer vip."""
        return self.put(self.vip_path % (vip), body=body)

    @APIParamsCall
    def delete_vip(self, vip):
        """Deletes the specified load balancer vip."""
        return self.delete(self.vip_path % (vip))

    @APIParamsCall
    def list_pools(self, retrieve_all=True, **_params):
        """Fetches a list of all load balancer pools for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('pools', self.pools_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_pool(self, pool, **_params):
        """Fetches information of a certain load balancer pool."""
        return self.get(self.pool_path % (pool), params=_params)

    @APIParamsCall
    def create_pool(self, body=None):
        """Creates a new load balancer pool."""
        return self.post(self.pools_path, body=body)

    @APIParamsCall
    def update_pool(self, pool, body=None):
        """Updates a load balancer pool."""
        return self.put(self.pool_path % (pool), body=body)

    @APIParamsCall
    def delete_pool(self, pool):
        """Deletes the specified load balancer pool."""
        return self.delete(self.pool_path % (pool))

    @APIParamsCall
    def retrieve_pool_stats(self, pool, **_params):
        """Retrieves stats for a certain load balancer pool."""
        return self.get(self.pool_path_stats % (pool), params=_params)

    @APIParamsCall
    def list_members(self, retrieve_all=True, **_params):
        """Fetches a list of all load balancer members for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('members', self.members_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_member(self, member, **_params):
        """Fetches information of a certain load balancer member."""
        return self.get(self.member_path % (member), params=_params)

    @APIParamsCall
    def create_member(self, body=None):
        """Creates a new load balancer member."""
        return self.post(self.members_path, body=body)

    @APIParamsCall
    def update_member(self, member, body=None):
        """Updates a load balancer member."""
        return self.put(self.member_path % (member), body=body)

    @APIParamsCall
    def delete_member(self, member):
        """Deletes the specified load balancer member."""
        return self.delete(self.member_path % (member))

    @APIParamsCall
    def list_health_monitors(self, retrieve_all=True, **_params):
        """Fetches a list of all load balancer health monitors for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('health_monitors', self.health_monitors_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_health_monitor(self, health_monitor, **_params):
        """Fetches information of a certain load balancer health monitor."""
        return self.get(self.health_monitor_path % (health_monitor),
                        params=_params)

    @APIParamsCall
    def create_health_monitor(self, body=None):
        """Creates a new load balancer health monitor."""
        return self.post(self.health_monitors_path, body=body)

    @APIParamsCall
    def update_health_monitor(self, health_monitor, body=None):
        """Updates a load balancer health monitor."""
        return self.put(self.health_monitor_path % (health_monitor), body=body)

    @APIParamsCall
    def delete_health_monitor(self, health_monitor):
        """Deletes the specified load balancer health monitor."""
        return self.delete(self.health_monitor_path % (health_monitor))

    @APIParamsCall
    def associate_health_monitor(self, pool, body):
        """Associate  specified load balancer health monitor and pool."""
        return self.post(self.associate_pool_health_monitors_path % (pool),
                         body=body)

    @APIParamsCall
    def disassociate_health_monitor(self, pool, health_monitor):
        """Disassociate specified load balancer health monitor and pool."""
        path = (self.disassociate_pool_health_monitors_path %
                {'pool': pool, 'health_monitor': health_monitor})
        return self.delete(path)

    @APIParamsCall
    def create_qos_queue(self, body=None):
        """Creates a new queue."""
        return self.post(self.qos_queues_path, body=body)

    @APIParamsCall
    def list_qos_queues(self, **_params):
        """Fetches a list of all queues for a tenant."""
        return self.get(self.qos_queues_path, params=_params)

    @APIParamsCall
    def show_qos_queue(self, queue, **_params):
        """Fetches information of a certain queue."""
        return self.get(self.qos_queue_path % (queue),
                        params=_params)

    @APIParamsCall
    def delete_qos_queue(self, queue):
        """Deletes the specified queue."""
        return self.delete(self.qos_queue_path % (queue))

    @APIParamsCall
    def list_agents(self, **_params):
        """Fetches agents."""
        # Pass filters in "params" argument to do_request
        return self.get(self.agents_path, params=_params)

    @APIParamsCall
    def show_agent(self, agent, **_params):
        """Fetches information of a certain agent."""
        return self.get(self.agent_path % (agent), params=_params)

    @APIParamsCall
    def update_agent(self, agent, body=None):
        """Updates an agent."""
        return self.put(self.agent_path % (agent), body=body)

    @APIParamsCall
    def delete_agent(self, agent):
        """Deletes the specified agent."""
        return self.delete(self.agent_path % (agent))

    @APIParamsCall
    def list_network_gateways(self, **_params):
        """Retrieve network gateways."""
        return self.get(self.network_gateways_path, params=_params)

    @APIParamsCall
    def show_network_gateway(self, gateway_id, **_params):
        """Fetch a network gateway."""
        return self.get(self.network_gateway_path % gateway_id, params=_params)

    @APIParamsCall
    def create_network_gateway(self, body=None):
        """Create a new network gateway."""
        return self.post(self.network_gateways_path, body=body)

    @APIParamsCall
    def update_network_gateway(self, gateway_id, body=None):
        """Update a network gateway."""
        return self.put(self.network_gateway_path % gateway_id, body=body)

    @APIParamsCall
    def delete_network_gateway(self, gateway_id):
        """Delete the specified network gateway."""
        return self.delete(self.network_gateway_path % gateway_id)

    @APIParamsCall
    def connect_network_gateway(self, gateway_id, body=None):
        """Connect a network gateway to the specified network."""
        base_uri = self.network_gateway_path % gateway_id
        return self.put("%s/connect_network" % base_uri, body=body)

    @APIParamsCall
    def disconnect_network_gateway(self, gateway_id, body=None):
        """Disconnect a network from the specified gateway."""
        base_uri = self.network_gateway_path % gateway_id
        return self.put("%s/disconnect_network" % base_uri, body=body)

    @APIParamsCall
    def list_gateway_devices(self, **_params):
        """Retrieve gateway devices."""
        return self.get(self.gateway_devices_path, params=_params)

    @APIParamsCall
    def show_gateway_device(self, gateway_device_id, **_params):
        """Fetch a gateway device."""
        return self.get(self.gateway_device_path % gateway_device_id,
                        params=_params)

    @APIParamsCall
    def create_gateway_device(self, body=None):
        """Create a new gateway device."""
        return self.post(self.gateway_devices_path, body=body)

    @APIParamsCall
    def update_gateway_device(self, gateway_device_id, body=None):
        """Updates a new gateway device."""
        return self.put(self.gateway_device_path % gateway_device_id,
                        body=body)

    @APIParamsCall
    def delete_gateway_device(self, gateway_device_id):
        """Delete the specified gateway device."""
        return self.delete(self.gateway_device_path % gateway_device_id)

    @APIParamsCall
    def list_dhcp_agent_hosting_networks(self, network, **_params):
        """Fetches a list of dhcp agents hosting a network."""
        return self.get((self.network_path + self.DHCP_AGENTS) % network,
                        params=_params)

    @APIParamsCall
    def list_networks_on_dhcp_agent(self, dhcp_agent, **_params):
        """Fetches a list of dhcp agents hosting a network."""
        return self.get((self.agent_path + self.DHCP_NETS) % dhcp_agent,
                        params=_params)

    @APIParamsCall
    def add_network_to_dhcp_agent(self, dhcp_agent, body=None):
        """Adds a network to dhcp agent."""
        return self.post((self.agent_path + self.DHCP_NETS) % dhcp_agent,
                         body=body)

    @APIParamsCall
    def remove_network_from_dhcp_agent(self, dhcp_agent, network_id):
        """Remove a network from dhcp agent."""
        return self.delete((self.agent_path + self.DHCP_NETS + "/%s") % (
            dhcp_agent, network_id))

    @APIParamsCall
    def list_l3_agent_hosting_routers(self, router, **_params):
        """Fetches a list of L3 agents hosting a router."""
        return self.get((self.router_path + self.L3_AGENTS) % router,
                        params=_params)

    @APIParamsCall
    def list_routers_on_l3_agent(self, l3_agent, **_params):
        """Fetches a list of L3 agents hosting a router."""
        return self.get((self.agent_path + self.L3_ROUTERS) % l3_agent,
                        params=_params)

    @APIParamsCall
    def add_router_to_l3_agent(self, l3_agent, body):
        """Adds a router to L3 agent."""
        return self.post((self.agent_path + self.L3_ROUTERS) % l3_agent,
                         body=body)

    @APIParamsCall
    def list_dragents_hosting_bgp_speaker(self, bgp_speaker, **_params):
        """Fetches a list of Dynamic Routing agents hosting a BGP speaker."""
        return self.get((self.bgp_speaker_path + self.BGP_DRAGENTS)
                        % bgp_speaker, params=_params)

    @APIParamsCall
    def add_bgp_speaker_to_dragent(self, bgp_dragent, body):
        """Adds a BGP speaker to Dynamic Routing agent."""
        return self.post((self.agent_path + self.BGP_DRINSTANCES)
                         % bgp_dragent, body=body)

    @APIParamsCall
    def remove_bgp_speaker_from_dragent(self, bgp_dragent, bgpspeaker_id):
        """Removes a BGP speaker from Dynamic Routing agent."""
        return self.delete((self.agent_path + self.BGP_DRINSTANCES + "/%s")
                           % (bgp_dragent, bgpspeaker_id))

    @APIParamsCall
    def list_bgp_speaker_on_dragent(self, bgp_dragent, **_params):
        """Fetches a list of BGP speakers hosted by Dynamic Routing agent."""
        return self.get((self.agent_path + self.BGP_DRINSTANCES)
                        % bgp_dragent, params=_params)

    @APIParamsCall
    def list_firewall_rules(self, retrieve_all=True, **_params):
        """Fetches a list of all firewall rules for a tenant."""
        # Pass filters in "params" argument to do_request

        return self.list('firewall_rules', self.firewall_rules_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_firewall_rule(self, firewall_rule, **_params):
        """Fetches information of a certain firewall rule."""
        return self.get(self.firewall_rule_path % (firewall_rule),
                        params=_params)

    @APIParamsCall
    def create_firewall_rule(self, body=None):
        """Creates a new firewall rule."""
        return self.post(self.firewall_rules_path, body=body)

    @APIParamsCall
    def update_firewall_rule(self, firewall_rule, body=None):
        """Updates a firewall rule."""
        return self.put(self.firewall_rule_path % (firewall_rule), body=body)

    @APIParamsCall
    def delete_firewall_rule(self, firewall_rule):
        """Deletes the specified firewall rule."""
        return self.delete(self.firewall_rule_path % (firewall_rule))

    @APIParamsCall
    def list_firewall_policies(self, retrieve_all=True, **_params):
        """Fetches a list of all firewall policies for a tenant."""
        # Pass filters in "params" argument to do_request

        return self.list('firewall_policies', self.firewall_policies_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_firewall_policy(self, firewall_policy, **_params):
        """Fetches information of a certain firewall policy."""
        return self.get(self.firewall_policy_path % (firewall_policy),
                        params=_params)

    @APIParamsCall
    def create_firewall_policy(self, body=None):
        """Creates a new firewall policy."""
        return self.post(self.firewall_policies_path, body=body)

    @APIParamsCall
    def update_firewall_policy(self, firewall_policy, body=None):
        """Updates a firewall policy."""
        return self.put(self.firewall_policy_path % (firewall_policy),
                        body=body)

    @APIParamsCall
    def delete_firewall_policy(self, firewall_policy):
        """Deletes the specified firewall policy."""
        return self.delete(self.firewall_policy_path % (firewall_policy))

    @APIParamsCall
    def firewall_policy_insert_rule(self, firewall_policy, body=None):
        """Inserts specified rule into firewall policy."""
        return self.put(self.firewall_policy_insert_path % (firewall_policy),
                        body=body)

    @APIParamsCall
    def firewall_policy_remove_rule(self, firewall_policy, body=None):
        """Removes specified rule from firewall policy."""
        return self.put(self.firewall_policy_remove_path % (firewall_policy),
                        body=body)

    @APIParamsCall
    def list_firewalls(self, retrieve_all=True, **_params):
        """Fetches a list of all firewalls for a tenant."""
        # Pass filters in "params" argument to do_request

        return self.list('firewalls', self.firewalls_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_firewall(self, firewall, **_params):
        """Fetches information of a certain firewall."""
        return self.get(self.firewall_path % (firewall), params=_params)

    @APIParamsCall
    def create_firewall(self, body=None):
        """Creates a new firewall."""
        return self.post(self.firewalls_path, body=body)

    @APIParamsCall
    def update_firewall(self, firewall, body=None):
        """Updates a firewall."""
        return self.put(self.firewall_path % (firewall), body=body)

    @APIParamsCall
    def delete_firewall(self, firewall):
        """Deletes the specified firewall."""
        return self.delete(self.firewall_path % (firewall))

    @APIParamsCall
    def remove_router_from_l3_agent(self, l3_agent, router_id):
        """Remove a router from l3 agent."""
        return self.delete((self.agent_path + self.L3_ROUTERS + "/%s") % (
            l3_agent, router_id))

    @APIParamsCall
    def get_lbaas_agent_hosting_pool(self, pool, **_params):
        """Fetches a loadbalancer agent hosting a pool."""
        return self.get((self.pool_path + self.LOADBALANCER_AGENT) % pool,
                        params=_params)

    @APIParamsCall
    def list_pools_on_lbaas_agent(self, lbaas_agent, **_params):
        """Fetches a list of pools hosted by the loadbalancer agent."""
        return self.get((self.agent_path + self.LOADBALANCER_POOLS) %
                        lbaas_agent, params=_params)

    @APIParamsCall
    def get_lbaas_agent_hosting_loadbalancer(self, loadbalancer, **_params):
        """Fetches a loadbalancer agent hosting a loadbalancer."""
        return self.get((self.lbaas_loadbalancer_path +
                         self.LOADBALANCER_HOSTING_AGENT) % loadbalancer,
                        params=_params)

    @APIParamsCall
    def list_loadbalancers_on_lbaas_agent(self, lbaas_agent, **_params):
        """Fetches a list of loadbalancers hosted by the loadbalancer agent."""
        return self.get((self.agent_path + self.AGENT_LOADBALANCERS) %
                        lbaas_agent, params=_params)

    @APIParamsCall
    def list_service_providers(self, retrieve_all=True, **_params):
        """Fetches service providers."""
        # Pass filters in "params" argument to do_request
        return self.list('service_providers', self.service_providers_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def create_metering_label(self, body=None):
        """Creates a metering label."""
        return self.post(self.metering_labels_path, body=body)

    @APIParamsCall
    def delete_metering_label(self, label):
        """Deletes the specified metering label."""
        return self.delete(self.metering_label_path % (label))

    @APIParamsCall
    def list_metering_labels(self, retrieve_all=True, **_params):
        """Fetches a list of all metering labels for a tenant."""
        return self.list('metering_labels', self.metering_labels_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_metering_label(self, metering_label, **_params):
        """Fetches information of a certain metering label."""
        return self.get(self.metering_label_path %
                        (metering_label), params=_params)

    @APIParamsCall
    def create_metering_label_rule(self, body=None):
        """Creates a metering label rule."""
        return self.post(self.metering_label_rules_path, body=body)

    @APIParamsCall
    def delete_metering_label_rule(self, rule):
        """Deletes the specified metering label rule."""
        return self.delete(self.metering_label_rule_path % (rule))

    @APIParamsCall
    def list_metering_label_rules(self, retrieve_all=True, **_params):
        """Fetches a list of all metering label rules for a label."""
        return self.list('metering_label_rules',
                         self.metering_label_rules_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_metering_label_rule(self, metering_label_rule, **_params):
        """Fetches information of a certain metering label rule."""
        return self.get(self.metering_label_rule_path %
                        (metering_label_rule), params=_params)

    @APIParamsCall
    def create_rbac_policy(self, body=None):
        """Create a new RBAC policy."""
        return self.post(self.rbac_policies_path, body=body)

    @APIParamsCall
    def update_rbac_policy(self, rbac_policy_id, body=None):
        """Update a RBAC policy."""
        return self.put(self.rbac_policy_path % rbac_policy_id, body=body)

    @APIParamsCall
    def list_rbac_policies(self, retrieve_all=True, **_params):
        """Fetch a list of all RBAC policies for a tenant."""
        return self.list('rbac_policies', self.rbac_policies_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_rbac_policy(self, rbac_policy_id, **_params):
        """Fetch information of a certain RBAC policy."""
        return self.get(self.rbac_policy_path % rbac_policy_id,
                        params=_params)

    @APIParamsCall
    def delete_rbac_policy(self, rbac_policy_id):
        """Delete the specified RBAC policy."""
        return self.delete(self.rbac_policy_path % rbac_policy_id)

    @APIParamsCall
    def list_qos_policies(self, retrieve_all=True, **_params):
        """Fetches a list of all qos policies for a tenant."""
        # Pass filters in "params" argument to do_request
        return self.list('policies', self.qos_policies_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_qos_policy(self, qos_policy, **_params):
        """Fetches information of a certain qos policy."""
        return self.get(self.qos_policy_path % qos_policy,
                        params=_params)

    @APIParamsCall
    def create_qos_policy(self, body=None):
        """Creates a new qos policy."""
        return self.post(self.qos_policies_path, body=body)

    @APIParamsCall
    def update_qos_policy(self, qos_policy, body=None):
        """Updates a qos policy."""
        return self.put(self.qos_policy_path % qos_policy,
                        body=body)

    @APIParamsCall
    def delete_qos_policy(self, qos_policy):
        """Deletes the specified qos policy."""
        return self.delete(self.qos_policy_path % qos_policy)

    @APIParamsCall
    def list_qos_rule_types(self, retrieve_all=True, **_params):
        """List available qos rule types."""
        return self.list('rule_types', self.qos_rule_types_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def list_bandwidth_limit_rules(self, policy_id,
                                   retrieve_all=True, **_params):
        """Fetches a list of all qos rules for the given policy."""
        return self.list('bandwidth_limit_rules',
                         self.qos_bandwidth_limit_rules_path % policy_id,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_bandwidth_limit_rule(self, rule, policy, body=None):
        """Fetches information of a certain bandwidth limit rule."""
        return self.get(self.qos_bandwidth_limit_rule_path %
                        (policy, rule), body=body)

    @APIParamsCall
    def create_bandwidth_limit_rule(self, policy, body=None):
        """Creates a new bandwidth limit rule."""
        return self.post(self.qos_bandwidth_limit_rules_path % policy,
                         body=body)

    @APIParamsCall
    def update_bandwidth_limit_rule(self, rule, policy, body=None):
        """Updates a bandwidth limit rule."""
        return self.put(self.qos_bandwidth_limit_rule_path %
                        (policy, rule), body=body)

    @APIParamsCall
    def delete_bandwidth_limit_rule(self, rule, policy):
        """Deletes a bandwidth limit rule."""
        return self.delete(self.qos_bandwidth_limit_rule_path %
                           (policy, rule))

    @APIParamsCall
    def create_flavor(self, body=None):
        """Creates a new Neutron service flavor."""
        return self.post(self.flavors_path, body=body)

    @APIParamsCall
    def delete_flavor(self, flavor):
        """Deletes the specified Neutron service flavor."""
        return self.delete(self.flavor_path % (flavor))

    @APIParamsCall
    def list_flavors(self, retrieve_all=True, **_params):
        """Fetches a list of all Neutron service flavors for a tenant."""
        return self.list('flavors', self.flavors_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_flavor(self, flavor, **_params):
        """Fetches information for a certain Neutron service flavor."""
        return self.get(self.flavor_path % (flavor), params=_params)

    @APIParamsCall
    def update_flavor(self, flavor, body):
        """Update a Neutron service flavor."""
        return self.put(self.flavor_path % (flavor), body=body)

    @APIParamsCall
    def associate_flavor(self, flavor, body):
        """Associate a Neutron service flavor with a profile."""
        return self.post(self.flavor_profile_bindings_path %
                         (flavor), body=body)

    @APIParamsCall
    def disassociate_flavor(self, flavor, flavor_profile):
        """Disassociate a Neutron service flavor with a profile."""
        return self.delete(self.flavor_profile_binding_path %
                           (flavor, flavor_profile))

    @APIParamsCall
    def create_service_profile(self, body=None):
        """Creates a new Neutron service flavor profile."""
        return self.post(self.service_profiles_path, body=body)

    @APIParamsCall
    def delete_service_profile(self, flavor_profile):
        """Deletes the specified Neutron service flavor profile."""
        return self.delete(self.service_profile_path % (flavor_profile))

    @APIParamsCall
    def list_service_profiles(self, retrieve_all=True, **_params):
        """Fetches a list of all Neutron service flavor profiles."""
        return self.list('service_profiles', self.service_profiles_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_service_profile(self, flavor_profile, **_params):
        """Fetches information for a certain Neutron service flavor profile."""
        return self.get(self.service_profile_path % (flavor_profile),
                        params=_params)

    @APIParamsCall
    def update_service_profile(self, service_profile, body):
        """Update a Neutron service profile."""
        return self.put(self.service_profile_path % (service_profile),
                        body=body)

    @APIParamsCall
    def list_availability_zones(self, retrieve_all=True, **_params):
        """Fetches a list of all availability zones."""
        return self.list('availability_zones', self.availability_zones_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def get_auto_allocated_topology(self, tenant_id, **_params):
        """Fetch information about a tenant's auto-allocated topology."""
        return self.get(
            self.auto_allocated_topology_path % tenant_id,
            params=_params)

    def validate_auto_allocated_topology_requirements(self, tenant_id):
        """Validate requirements for getting an auto-allocated topology."""
        return self.get_auto_allocated_topology(tenant_id, fields=['dry-run'])

    @APIParamsCall
    def list_bgp_speakers(self, retrieve_all=True, **_params):
        """Fetches a list of all BGP speakers for a tenant."""
        return self.list('bgp_speakers', self.bgp_speakers_path, retrieve_all,
                         **_params)

    @APIParamsCall
    def show_bgp_speaker(self, bgp_speaker_id, **_params):
        """Fetches information of a certain BGP speaker."""
        return self.get(self.bgp_speaker_path % (bgp_speaker_id),
                        params=_params)

    @APIParamsCall
    def create_bgp_speaker(self, body=None):
        """Creates a new BGP speaker."""
        return self.post(self.bgp_speakers_path, body=body)

    @APIParamsCall
    def update_bgp_speaker(self, bgp_speaker_id, body=None):
        """Update a BGP speaker."""
        return self.put(self.bgp_speaker_path % bgp_speaker_id, body=body)

    @APIParamsCall
    def delete_bgp_speaker(self, speaker_id):
        """Deletes the specified BGP speaker."""
        return self.delete(self.bgp_speaker_path % (speaker_id))

    @APIParamsCall
    def add_peer_to_bgp_speaker(self, speaker_id, body=None):
        """Adds a peer to BGP speaker."""
        return self.put((self.bgp_speaker_path % speaker_id) +
                        "/add_bgp_peer", body=body)

    @APIParamsCall
    def remove_peer_from_bgp_speaker(self, speaker_id, body=None):
        """Removes a peer from BGP speaker."""
        return self.put((self.bgp_speaker_path % speaker_id) +
                        "/remove_bgp_peer", body=body)

    @APIParamsCall
    def add_network_to_bgp_speaker(self, speaker_id, body=None):
        """Adds a network to BGP speaker."""
        return self.put((self.bgp_speaker_path % speaker_id) +
                        "/add_gateway_network", body=body)

    @APIParamsCall
    def remove_network_from_bgp_speaker(self, speaker_id, body=None):
        """Removes a network from BGP speaker."""
        return self.put((self.bgp_speaker_path % speaker_id) +
                        "/remove_gateway_network", body=body)

    @APIParamsCall
    def list_route_advertised_from_bgp_speaker(self, speaker_id, **_params):
        """Fetches a list of all routes advertised by BGP speaker."""
        return self.get((self.bgp_speaker_path % speaker_id) +
                        "/get_advertised_routes", params=_params)

    @APIParamsCall
    def list_bgp_peers(self, **_params):
        """Fetches a list of all BGP peers."""
        return self.get(self.bgp_peers_path, params=_params)

    @APIParamsCall
    def show_bgp_peer(self, peer_id, **_params):
        """Fetches information of a certain BGP peer."""
        return self.get(self.bgp_peer_path % peer_id,
                        params=_params)

    @APIParamsCall
    def create_bgp_peer(self, body=None):
        """Create a new BGP peer."""
        return self.post(self.bgp_peers_path, body=body)

    @APIParamsCall
    def update_bgp_peer(self, bgp_peer_id, body=None):
        """Update a BGP peer."""
        return self.put(self.bgp_peer_path % bgp_peer_id, body=body)

    @APIParamsCall
    def delete_bgp_peer(self, peer_id):
        """Deletes the specified BGP peer."""
        return self.delete(self.bgp_peer_path % peer_id)

    @APIParamsCall
    def list_network_ip_availabilities(self, retrieve_all=True, **_params):
        """Fetches IP availibility information for all networks"""
        return self.list('network_ip_availabilities',
                         self.network_ip_availabilities_path,
                         retrieve_all, **_params)

    @APIParamsCall
    def show_network_ip_availability(self, network, **_params):
        """Fetches IP availability information for a specified network"""
        return self.get(self.network_ip_availability_path % (network),
                        params=_params)

    @APIParamsCall
    def add_tag(self, resource_type, resource_id, tag, **_params):
        """Add a tag on the resource."""
        return self.put(self.tag_path % (resource_type, resource_id, tag))

    @APIParamsCall
    def replace_tag(self, resource_type, resource_id, body, **_params):
        """Replace tags on the resource."""
        return self.put(self.tags_path % (resource_type, resource_id), body)

    @APIParamsCall
    def remove_tag(self, resource_type, resource_id, tag, **_params):
        """Remove a tag on the resource."""
        return self.delete(self.tag_path % (resource_type, resource_id, tag))

    @APIParamsCall
    def remove_tag_all(self, resource_type, resource_id, **_params):
        """Remove all tags on the resource."""
        return self.delete(self.tags_path % (resource_type, resource_id))

    def __init__(self, **kwargs):
        """Initialize a new client for the Neutron v2.0 API."""
        super(Client, self).__init__(**kwargs)
        self._register_extensions(self.version)

    def extend_show(self, resource_singular, path, parent_resource):
        def _fx(obj, **_params):
            return self.show_ext(path, obj, **_params)

        def _parent_fx(obj, parent_id, **_params):
            return self.show_ext(path % parent_id, obj, **_params)
        fn = _fx if not parent_resource else _parent_fx
        setattr(self, "show_%s" % resource_singular, fn)

    def extend_list(self, resource_plural, path, parent_resource):
        def _fx(retrieve_all=True, **_params):
            return self.list_ext(resource_plural, path,
                                 retrieve_all, **_params)

        def _parent_fx(parent_id, retrieve_all=True, **_params):
            return self.list_ext(resource_plural, path % parent_id,
                                 retrieve_all, **_params)
        fn = _fx if not parent_resource else _parent_fx
        setattr(self, "list_%s" % resource_plural, fn)

    def extend_create(self, resource_singular, path, parent_resource):
        def _fx(body=None):
            return self.create_ext(path, body)

        def _parent_fx(parent_id, body=None):
            return self.create_ext(path % parent_id, body)
        fn = _fx if not parent_resource else _parent_fx
        setattr(self, "create_%s" % resource_singular, fn)

    def extend_delete(self, resource_singular, path, parent_resource):
        def _fx(obj):
            return self.delete_ext(path, obj)

        def _parent_fx(obj, parent_id):
            return self.delete_ext(path % parent_id, obj)
        fn = _fx if not parent_resource else _parent_fx
        setattr(self, "delete_%s" % resource_singular, fn)

    def extend_update(self, resource_singular, path, parent_resource):
        def _fx(obj, body=None):
            return self.update_ext(path, obj, body)

        def _parent_fx(obj, parent_id, body=None):
            return self.update_ext(path % parent_id, obj, body)
        fn = _fx if not parent_resource else _parent_fx
        setattr(self, "update_%s" % resource_singular, fn)

    def _extend_client_with_module(self, module, version):
        classes = inspect.getmembers(module, inspect.isclass)
        for cls_name, cls in classes:
            if hasattr(cls, 'versions'):
                if version not in cls.versions:
                    continue
            parent_resource = getattr(cls, 'parent_resource', None)
            if issubclass(cls, client_extension.ClientExtensionList):
                self.extend_list(cls.resource_plural, cls.object_path,
                                 parent_resource)
            elif issubclass(cls, client_extension.ClientExtensionCreate):
                self.extend_create(cls.resource, cls.object_path,
                                   parent_resource)
            elif issubclass(cls, client_extension.ClientExtensionUpdate):
                self.extend_update(cls.resource, cls.resource_path,
                                   parent_resource)
            elif issubclass(cls, client_extension.ClientExtensionDelete):
                self.extend_delete(cls.resource, cls.resource_path,
                                   parent_resource)
            elif issubclass(cls, client_extension.ClientExtensionShow):
                self.extend_show(cls.resource, cls.resource_path,
                                 parent_resource)
            elif issubclass(cls, client_extension.NeutronClientExtension):
                setattr(self, "%s_path" % cls.resource_plural,
                        cls.object_path)
                setattr(self, "%s_path" % cls.resource, cls.resource_path)
                self.EXTED_PLURALS.update({cls.resource_plural: cls.resource})

    def _register_extensions(self, version):
        for name, module in itertools.chain(
                client_extension._discover_via_entry_points()):
            self._extend_client_with_module(module, version)
