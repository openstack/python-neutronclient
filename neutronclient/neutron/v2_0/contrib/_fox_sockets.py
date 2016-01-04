# Copyright 2015 Rackspace Hosting Inc.
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

from neutronclient._i18n import _
from neutronclient.common import extension


def _add_updatable_args(parser):
    parser.add_argument(
        'name',
        help=_('Name of this fox socket.'))


def _updatable_args2body(parsed_args, body, client):
    if parsed_args.name:
        body['name'] = parsed_args.name


class FoxInSocket(extension.NeutronClientExtension):
    """Define required variables for resource operations."""

    resource = 'fox_socket'
    resource_plural = '%ss' % resource
    object_path = '/%s' % resource_plural
    resource_path = '/%s/%%s' % resource_plural
    versions = ['2.0']


class FoxInSocketsList(extension.ClientExtensionList, FoxInSocket):
    """List fox sockets."""

    shell_command = 'fox-sockets-list'
    list_columns = ['id', 'name']
    pagination_support = True
    sorting_support = True


class FoxInSocketsCreate(extension.ClientExtensionCreate, FoxInSocket):
    """Create a fox socket."""

    shell_command = 'fox-sockets-create'
    list_columns = ['id', 'name']

    def add_known_arguments(self, parser):
        _add_updatable_args(parser)

    def args2body(self, parsed_args):
        body = {}
        client = self.get_client()
        _updatable_args2body(parsed_args, body, client)
        return {'fox_socket': body}


class FoxInSocketsUpdate(extension.ClientExtensionUpdate, FoxInSocket):
    """Update a fox socket."""

    shell_command = 'fox-sockets-update'
    list_columns = ['id', 'name']

    def add_known_arguments(self, parser):
        # _add_updatable_args(parser)
        parser.add_argument(
            '--name',
            help=_('Name of this fox socket.'))

    def args2body(self, parsed_args):
        body = {'name': parsed_args.name}
        return {'fox_socket': body}


class FoxInSocketsDelete(extension.ClientExtensionDelete, FoxInSocket):
    """Delete a fox socket."""

    shell_command = 'fox-sockets-delete'


class FoxInSocketsShow(extension.ClientExtensionShow, FoxInSocket):
    """Show a fox socket."""

    shell_command = 'fox-sockets-show'
