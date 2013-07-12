# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from neutronclient.neutron import v2_0 as neutronV20


class ListCredential(neutronV20.ListCommand):
    """List credentials that belong to a given tenant."""

    resource = 'credential'
    log = logging.getLogger(__name__ + '.ListCredential')
    _formatters = {}
    list_columns = ['credential_id', 'credential_name', 'user_name',
                    'password', 'type']


class ShowCredential(neutronV20.ShowCommand):
    """Show information of a given credential."""

    resource = 'credential'
    log = logging.getLogger(__name__ + '.ShowCredential')
    allow_names = False


class CreateCredential(neutronV20.CreateCommand):
    """Creates a credential."""

    resource = 'credential'
    log = logging.getLogger(__name__ + '.CreateCredential')

    def add_known_arguments(self, parser):
        parser.add_argument(
            'credential_name',
            help='Name/Ip address for Credential')
        parser.add_argument(
            'credential_type',
            help='Type of the Credential')
        parser.add_argument(
            '--username',
            help='Username for the credential')
        parser.add_argument(
            '--password',
            help='Password for the credential')

    def args2body(self, parsed_args):
        body = {'credential': {
            'credential_name': parsed_args.credential_name}}

        if parsed_args.credential_type:
            body['credential'].update({'type':
                                      parsed_args.credential_type})
        if parsed_args.username:
            body['credential'].update({'user_name':
                                      parsed_args.username})
        if parsed_args.password:
            body['credential'].update({'password':
                                      parsed_args.password})
        return body


class DeleteCredential(neutronV20.DeleteCommand):
    """Delete a  given credential."""

    log = logging.getLogger(__name__ + '.DeleteCredential')
    resource = 'credential'
    allow_names = False
