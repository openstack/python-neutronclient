# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Citrix Systems
# All Rights Reserved.
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
#    @author: Tyler Smith, Cisco Systems

import logging
import httplib
import socket
import time
import urllib

from quantum.common import exceptions
from quantum.common.serializer import Serializer

LOG = logging.getLogger('quantum.client')
AUTH_TOKEN_HEADER = "X-Auth-Token"


def exception_handler_v10(status_code, error_content):
    """ Exception handler for API v1.0 client

        This routine generates the appropriate
        Quantum exception according to the contents of the
        response body

        :param status_code: HTTP error status code
        :param error_content: deserialized body of error response
    """

    quantum_error_types = {
        420: 'networkNotFound',
        421: 'networkInUse',
        430: 'portNotFound',
        431: 'requestedStateInvalid',
        432: 'portInUse',
        440: 'alreadyAttached'
        }

    quantum_errors = {
        400: exceptions.BadInputError,
        401: exceptions.NotAuthorized,
        404: exceptions.NotFound,
        420: exceptions.NetworkNotFoundClient,
        421: exceptions.NetworkInUseClient,
        430: exceptions.PortNotFoundClient,
        431: exceptions.StateInvalidClient,
        432: exceptions.PortInUseClient,
        440: exceptions.AlreadyAttachedClient,
        501: NotImplementedError
        }

    # Find real error type
    error_type = None
    if isinstance(error_content, dict):
        error_type = quantum_error_types.get(status_code)
    if error_type:
        error_dict = error_content[error_type]
        error_message = error_dict['message'] + "\n" +\
                        error_dict['detail']
    else:
        error_message = error_content
    # raise the appropriate error!
    ex = quantum_errors[status_code](message=error_message)
    ex.args = ([dict(status_code=status_code,
                     message=error_message)],)
    raise ex


def exception_handler_v11(status_code, error_content):
    """ Exception handler for API v1.1 client

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
        'AlreadyAttached': exceptions.AlreadyAttachedClient,
        }

    error_dict = None
    if isinstance(error_content, dict):
        error_dict = error_content.get('QuantumError')
    # Find real error type
    if error_dict:
        # If QuantumError key is found, it will definitely contain
        # a 'message' and 'type' keys
        error_type = error_dict['type']
        error_message = (error_dict['message'] + "\n" +
                         error_dict['detail'])
        # raise the appropriate error!
        ex = quantum_errors[error_type](message=error_message)
        ex.args = ([dict(status_code=status_code,
                         message=error_message)],)
        raise ex
    # If we end up here the exception was not a quantum error
    msg = "%s-%s" % (status_code, error_content)
    raise exceptions.QuantumClientException(message=msg)


EXCEPTION_HANDLERS = {
    '1.0': exception_handler_v10,
    '1.1': exception_handler_v11
}


class ApiCall(object):
    """A Decorator to add support for format and tenant overriding"""
    def __init__(self, function):
        self.function = function

    def __get__(self, instance, owner):
        def with_params(*args, **kwargs):
            """
            Temporarily sets the format and tenant for this request
            """
            (format, tenant) = (instance.format, instance.tenant)

            if 'format' in kwargs:
                instance.format = kwargs['format']
            if 'tenant' in kwargs:
                instance.tenant = kwargs['tenant']

            ret = self.function(instance, *args)
            (instance.format, instance.tenant) = (format, tenant)
            return ret
        return with_params


class Client(object):

    """A base client class - derived from Glance.BaseClient"""

    #Metadata for deserializing xml
    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "network": ["id", "name"],
                "port": ["id", "state"],
                "attachment": ["id"]},
            "plurals": {"networks": "network",
                        "ports": "port"}},
    }

    # Action query strings
    networks_path = "/networks"
    network_path = "/networks/%s"
    ports_path = "/networks/%s/ports"
    port_path = "/networks/%s/ports/%s"
    attachment_path = "/networks/%s/ports/%s/attachment"
    detail_path = "/detail"

    def __init__(self, host="127.0.0.1", port=9696, use_ssl=False, tenant=None,
                 format="xml", testingStub=None, key_file=None, cert_file=None,
                 auth_token=None, logger=None,
                 version="1.1",
                 uri_prefix="/tenants/{tenant_id}",
                 retries=0,
                 retry_interval=1):
        """
        Creates a new client to some service.

        :param host: The host where service resides
        :param port: The port where service resides
        :param use_ssl: True to use SSL, False to use HTTP
        :param tenant: The tenant ID to make requests with
        :param format: The format to query the server with
        :param testingStub: A class that stubs basic server methods for tests
        :param key_file: The SSL key file to use if use_ssl is true
        :param cert_file: The SSL cert file to use if use_ssl is true
        :param auth_token: authentication token to be passed to server
        :param logger: Logger object for the client library
        :param action_prefix: prefix for request URIs
        :param retries: How many times to retry a failed connection attempt
        :param retry_interval: The # of seconds between connection attempts
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.tenant = tenant
        self.format = format
        self.connection = None
        self.testingStub = testingStub
        self.key_file = key_file
        self.cert_file = cert_file
        self.logger = logger
        self.auth_token = auth_token
        self.version = version
        self.action_prefix = "/v%s%s" % (version, uri_prefix)
        self.retries = retries
        self.retry_interval = retry_interval

    def _handle_fault_response(self, status_code, response_body):
        # Create exception with HTTP status code and message
        error_message = response_body
        LOG.debug("Server returned error: %s", status_code)
        LOG.debug("Error message: %s", error_message)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = Serializer().deserialize(error_message,
                                                      self.content_type())
        except:
            # If unable to deserialized body it is probably not a
            # Quantum error
            des_error_body = {'message': error_message}
        # Raise the appropriate exception
        EXCEPTION_HANDLERS[self.version](status_code, des_error_body)

    def get_connection_type(self):
        """
        Returns the proper connection type
        """
        if self.testingStub:
            return self.testingStub
        if self.use_ssl:
            return httplib.HTTPSConnection
        else:
            return httplib.HTTPConnection

    def _send_request(self, conn, method, action, body, headers):
        # Salvatore: Isolating this piece of code in its own method to
        # facilitate stubout for testing
        if self.logger:
            self.logger.debug("Quantum Client Request:\n" \
                    + method + " " + action + "\n")
            if body:
                self.logger.debug(body)
        conn.request(method, action, body, headers)
        return conn.getresponse()

    def do_request(self, method, action, body=None,
                   headers=None, params=None):
        """
        Connects to the server and issues a request.
        Returns the result data, or raises an appropriate exception if
        HTTP status code is not 2xx

        :param method: HTTP method ("GET", "POST", "PUT", etc...)
        :param body: string of data to send, or None (default)
        :param headers: mapping of key/value pairs to add as headers
        :param params: dictionary of key/value pairs to add to append
                             to action
        :raises: ConnectionFailed
        """
        LOG.debug("Client issuing request: %s", action)
        # Ensure we have a tenant id
        if not self.tenant:
            raise Exception("Tenant ID not set")
        # Add format and tenant_id
        action += ".%s" % self.format
        action = self.action_prefix + action
        action = action.replace('{tenant_id}', self.tenant)

        if type(params) is dict:
            action += '?' + urllib.urlencode(params)
        if body:
            body = self.serialize(body)
        try:
            connection_type = self.get_connection_type()
            headers = headers or {"Content-Type":
                                      "application/%s" % self.format}
            # if available, add authentication token
            if self.auth_token:
                headers[AUTH_TOKEN_HEADER] = self.auth_token
            # Open connection and send request, handling SSL certs
            certs = {'key_file': self.key_file, 'cert_file': self.cert_file}
            certs = dict((x, certs[x]) for x in certs if certs[x] != None)
            if self.use_ssl and len(certs):
                conn = connection_type(self.host, self.port, **certs)
            else:
                conn = connection_type(self.host, self.port)
            res = self._send_request(conn, method, action, body, headers)
            status_code = self.get_status_code(res)
            data = res.read()
            if self.logger:
                self.logger.debug("Quantum Client Reply (code = %s) :\n %s" \
                        % (str(status_code), data))
            if status_code in (httplib.OK,
                               httplib.CREATED,
                               httplib.ACCEPTED,
                               httplib.NO_CONTENT):
                return self.deserialize(data, status_code)
            else:
                self._handle_fault_response(status_code, data)
        except (socket.error, IOError), e:
            exc = exceptions.ConnectionFailed(reason=str(e))
            LOG.exception(exc.message)
            raise exc

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
            return Serializer().serialize(data, self.content_type())
        else:
            raise Exception("unable to serialize object of type = '%s'" \
                                % type(data))

    def deserialize(self, data, status_code):
        """
        Deserializes a an xml or json string into a dictionary
        """
        if status_code == 204:
            return data
        return Serializer(self._serialization_metadata).\
                    deserialize(data, self.content_type())

    def content_type(self, format=None):
        """
        Returns the mime-type for either 'xml' or 'json'.  Defaults to the
        currently set format
        """
        if not format:
            format = self.format
        return "application/%s" % (format)

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
                    LOG.debug(_('Retrying connection to quantum service'))
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

    @ApiCall
    def list_networks(self):
        """
        Fetches a list of all networks for a tenant
        """
        return self.get(self.networks_path)

    @ApiCall
    def list_networks_details(self):
        """
        Fetches a detailed list of all networks for a tenant
        """
        return self.get(self.networks_path + self.detail_path)

    @ApiCall
    def show_network(self, network):
        """
        Fetches information of a certain network
        """
        return self.get(self.network_path % (network))

    @ApiCall
    def show_network_details(self, network):
        """
        Fetches the details of a certain network
        """
        return self.get((self.network_path + self.detail_path) % (network))

    @ApiCall
    def create_network(self, body=None):
        """
        Creates a new network
        """
        return self.post(self.networks_path, body=body)

    @ApiCall
    def update_network(self, network, body=None):
        """
        Updates a network
        """
        return self.put(self.network_path % (network), body=body)

    @ApiCall
    def delete_network(self, network):
        """
        Deletes the specified network
        """
        return self.delete(self.network_path % (network))

    @ApiCall
    def list_ports(self, network):
        """
        Fetches a list of ports on a given network
        """
        return self.get(self.ports_path % (network))

    @ApiCall
    def list_ports_details(self, network):
        """
        Fetches a detailed list of ports on a given network
        """
        return self.get((self.ports_path + self.detail_path) % (network))

    @ApiCall
    def show_port(self, network, port):
        """
        Fetches the information of a certain port
        """
        return self.get(self.port_path % (network, port))

    @ApiCall
    def show_port_details(self, network, port):
        """
        Fetches the details of a certain port
        """
        return self.get((self.port_path + self.detail_path) % (network, port))

    @ApiCall
    def create_port(self, network, body=None):
        """
        Creates a new port on a given network
        """
        return self.post(self.ports_path % (network), body=body)

    @ApiCall
    def delete_port(self, network, port):
        """
        Deletes the specified port from a network
        """
        return self.delete(self.port_path % (network, port))

    @ApiCall
    def update_port(self, network, port, body=None):
        """
        Sets the attributes of the specified port
        """
        return self.put(self.port_path % (network, port), body=body)

    @ApiCall
    def show_port_attachment(self, network, port):
        """
        Fetches the attachment-id associated with the specified port
        """
        return self.get(self.attachment_path % (network, port))

    @ApiCall
    def attach_resource(self, network, port, body=None):
        """
        Sets the attachment-id of the specified port
        """
        return self.put(self.attachment_path % (network, port), body=body)

    @ApiCall
    def detach_resource(self, network, port):
        """
        Removes the attachment-id of the specified port
        """
        return self.delete(self.attachment_path % (network, port))


class ClientV11(Client):
    """
    This class overiddes some methods of the Client class in order to deal with
    features specific to API v1.1 such as filters
    """

    @ApiCall
    def list_networks(self, **filters):
        """
        Fetches a list of all networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.networks_path, params=filters)

    @ApiCall
    def list_networks_details(self, **filters):
        """
        Fetches a detailed list of all networks for a tenant
        """
        return self.get(self.networks_path + self.detail_path, params=filters)

    @ApiCall
    def list_ports(self, network, **filters):
        """
        Fetches a list of ports on a given network
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.ports_path % (network), params=filters)

    @ApiCall
    def list_ports_details(self, network, **filters):
        """
        Fetches a detailed list of ports on a given network
        """
        return self.get((self.ports_path + self.detail_path) % (network),
                        params=filters)
