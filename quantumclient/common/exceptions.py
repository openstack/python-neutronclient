# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Nicira Networks, Inc
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

from quantumclient.common import _

"""
Quantum base exception handling.
"""


class QuantumException(Exception):
    """Base Quantum Exception

    Taken from nova.exception.NovaException
    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")

    def __init__(self, **kwargs):
        try:
            self._error_string = self.message % kwargs

        except Exception:
            # at least get the core message out if something happened
            self._error_string = self.message

    def __str__(self):
        return self._error_string


class NotFound(QuantumException):
    pass


class QuantumClientException(QuantumException):

    def __init__(self, **kwargs):
        message = kwargs.get('message')
        self.status_code = kwargs.get('status_code', 0)
        if message:
            self.message = message
        super(QuantumClientException, self).__init__(**kwargs)


# NOTE: on the client side, we use different exception types in order
# to allow client library users to handle server exceptions in try...except
# blocks. The actual error message is the one generated on the server side
class NetworkNotFoundClient(QuantumClientException):
    pass


class PortNotFoundClient(QuantumClientException):
    pass


class MalformedResponseBody(QuantumException):
    message = _("Malformed response body: %(reason)s")


class StateInvalidClient(QuantumClientException):
    pass


class NetworkInUseClient(QuantumClientException):
    pass


class PortInUseClient(QuantumClientException):
    pass


class AlreadyAttachedClient(QuantumClientException):
    pass


class Unauthorized(QuantumClientException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    pass


class Forbidden(QuantumClientException):
    """
    HTTP 403 - Forbidden: your credentials don't give you access to this
    resource.
    """
    pass


class EndpointNotFound(QuantumClientException):
    """Could not find Service or Region in Service Catalog."""
    pass


class AmbiguousEndpoints(QuantumClientException):
    """Found more than one matching endpoint in Service Catalog."""

    def __str__(self):
        return "AmbiguousEndpoints: %s" % repr(self.message)


class QuantumCLIError(QuantumClientException):
    """ Exception raised when command line parsing fails """
    pass


class ConnectionFailed(QuantumClientException):
    message = _("Connection to quantum failed: %(reason)s")


class BadInputError(Exception):
    """Error resulting from a client sending bad input to a server"""
    pass


class Error(Exception):
    def __init__(self, message=None):
        super(Error, self).__init__(message)


class MalformedRequestBody(QuantumException):
    message = _("Malformed request body: %(reason)s")


class Invalid(Error):
    pass


class InvalidContentType(Invalid):
    message = _("Invalid content type %(content_type)s.")


class UnsupportedVersion(Exception):
    """Indicates that the user is trying to use an unsupported
       version of the API"""
    pass


class CommandError(Exception):
    pass
