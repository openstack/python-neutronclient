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

import os

from six.moves import configparser
from tempest_lib.cli import base


_CREDS_FILE = 'functional_creds.conf'


def credentials():
    """Retrieves credentials to run functional tests

    Credentials are either read from the environment or from a config file
    ('functional_creds.conf'). Environment variables override those from the
    config file.

    The 'functional_creds.conf' file is the clean and new way to use (by
    default tox 2.0 does not pass environment variables).
    """

    username = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    tenant_name = os.environ.get('OS_TENANT_NAME')
    auth_url = os.environ.get('OS_AUTH_URL')

    config = configparser.RawConfigParser()
    if config.read(_CREDS_FILE):
        username = username or config.get('admin', 'user')
        password = password or config.get('admin', 'pass')
        tenant_name = tenant_name or config.get('admin', 'tenant')
        auth_url = auth_url or config.get('auth', 'uri')

    return {
        'username': username,
        'password': password,
        'tenant_name': tenant_name,
        'auth_url': auth_url
    }


class ClientTestBase(base.ClientTestBase):
    """This is a first pass at a simple read only python-neutronclient test.
    This only exercises client commands that are read only.

    This should test commands:
    * as a regular user
    * as a admin user
    * with and without optional parameters
    * initially just check return codes, and later test command outputs

    """

    def _get_clients(self):
        creds = credentials()
        cli_dir = os.environ.get(
            'OS_NEUTRONCLIENT_EXEC_DIR',
            os.path.join(os.path.abspath('.'), '.tox/functional/bin'))
        return base.CLIClient(username=creds['username'],
                              password=creds['password'],
                              tenant_name=creds['tenant_name'],
                              uri=creds['auth_url'],
                              cli_dir=cli_dir)

    def neutron(self, *args, **kwargs):
        return self.clients.neutron(*args,
                                    **kwargs)
