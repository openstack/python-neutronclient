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

import os_client_config
from tempest.lib.cli import base


def credentials(cloud='devstack-admin'):
    """Retrieves credentials to run functional tests

    Credentials are either read via os-client-config from the environment
    or from a config file ('clouds.yaml'). Environment variables override
    those from the config file.

    devstack produces a clouds.yaml with two named clouds - one named
    'devstack' which has user privs and one named 'devstack-admin' which
    has admin privs. This function will default to getting the devstack-admin
    cloud as that is the current expected behavior.
    """
    return get_cloud_config(cloud=cloud).get_auth_args()


def get_cloud_config(cloud='devstack-admin'):
    return os_client_config.OpenStackConfig().get_one_cloud(cloud=cloud)


class ClientTestBase(base.ClientTestBase):
    """This is a first pass at a simple read only python-neutronclient test.

    This only exercises client commands that are read only.
    This should test commands:
    * as a regular user
    * as an admin user
    * with and without optional parameters
    * initially just check return codes, and later test command outputs

    """

    def _get_clients_from_os_cloud_config(self, cloud='devstack-admin'):
        creds = credentials(cloud)
        cli_dir = os.environ.get(
            'OS_NEUTRONCLIENT_EXEC_DIR',
            os.path.join(os.path.abspath('.'), '.tox/functional/bin'))

        return base.CLIClient(
            username=creds['username'],
            password=creds['password'],
            tenant_name=creds['project_name'],
            project_domain_id=creds['project_domain_id'],
            user_domain_id=creds['user_domain_id'],
            uri=creds['auth_url'],
            cli_dir=cli_dir)

    def _get_clients(self):
        return self._get_clients_from_os_cloud_config()

    def neutron(self, *args, **kwargs):
        return self.clients.neutron(*args, **kwargs)

    def neutron_non_admin(self, *args, **kwargs):
        if not hasattr(self, '_non_admin_clients'):
            self._non_admin_clients = self._get_clients_from_os_cloud_config(
                cloud='devstack')
        return self._non_admin_clients.neutron(*args, **kwargs)

    def is_extension_enabled(self, extension_alias):
        extensions = self.parser.listing(self.neutron('ext-list'))
        aliases = [e['alias'] for e in extensions]
        return extension_alias in aliases
