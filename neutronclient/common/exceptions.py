# Copyright 2011 VMware, Inc
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

from neutronclient.common import _

"""
Neutron base exception handling.
"""


class NeutronException(Exception):
    """Base Neutron Exception

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


class NotFound(NeutronException):
    pass


class NeutronClientException(NeutronException):

    def __init__(self, **kwargs):
        message = kwargs.get('message')
        self.status_code = kwargs.get('status_code', 0)
        if message:
            self.message = message
        super(NeutronClientException, self).__init__(**kwargs)


# NOTE: on the client side, we use different exception types in order
# to allow client library users to handle server exceptions in try...except
# blocks. The actual error message is the one generated on the server side
class NetworkNotFoundClient(NeutronClientException):
    pass


class PortNotFoundClient(NeutronClientException):
    pass


class MalformedResponseBody(NeutronException):
    message = _("Malformed response body: %(reason)s")


class StateInvalidClient(NeutronClientException):
    pass


class NetworkInUseClient(NeutronClientException):
    pass


class PortInUseClient(NeutronClientException):
    pass


class IpAddressInUseClient(NeutronClientException):
    pass


class AlreadyAttachedClient(NeutronClientException):
    pass


class IpAddressGenerationFailureClient(NeutronClientException):
    pass


class ExternalIpAddressExhaustedClient(NeutronClientException):
    pass


class Unauthorized(NeutronClientException):
    message = _("Unauthorized: bad credentials.")


class Forbidden(NeutronClientException):
    message = _("Forbidden: your credentials don't give you access to this "
                "resource.")


class EndpointNotFound(NeutronClientException):
    """Could not find Service or Region in Service Catalog."""
    message = _("Could not find Service or Region in Service Catalog.")


class EndpointTypeNotFound(NeutronClientException):
    """Could not find endpoint type in Service Catalog."""

    def __str__(self):
        msg = _("Could not find endpoint type %s in Service Catalog.")
        return msg % repr(self.message)


class AmbiguousEndpoints(NeutronClientException):
    """Found more than one matching endpoint in Service Catalog."""

    def __str__(self):
        return _("AmbiguousEndpoints: %s") % repr(self.message)


class NeutronCLIError(NeutronClientException):
    """Exception raised when command line parsing fails."""
    pass


class RequestURITooLong(NeutronClientException):
    """Raised when a request fails with HTTP error 414."""

    def __init__(self, **kwargs):
        self.excess = kwargs.get('excess', 0)
        super(RequestURITooLong, self).__init__(**kwargs)


class ConnectionFailed(NeutronClientException):
    message = _("Connection to neutron failed: %(reason)s")


class BadInputError(Exception):
    """Error resulting from a client sending bad input to a server."""
    pass


class Error(Exception):
    def __init__(self, message=None):
        super(Error, self).__init__(message)


class MalformedRequestBody(NeutronException):
    message = _("Malformed request body: %(reason)s")


class Invalid(Error):
    pass


class InvalidContentType(Invalid):
    message = _("Invalid content type %(content_type)s.")


class UnsupportedVersion(Exception):
    """Indicates that the user is trying to use an unsupported
       version of the API
    """
    pass


class CommandError(Exception):
    pass


class NeutronClientNoUniqueMatch(NeutronClientException):
    message = _("Multiple %(resource)s matches found for name '%(name)s',"
                " use an ID to be more specific.")


class SslCertificateValidationError(NeutronClientException):
    message = _("SSL certificate validation has failed: %(reason)s")
