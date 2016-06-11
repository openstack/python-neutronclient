# Copyright 2016 Cisco Systems
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutronclient.tests.functional import base

from tempest.lib import exceptions


class PurgeNeutronClientCLITest(base.ClientTestBase):

    def _safe_cleanup(self, delete_command):
        try:
            self.neutron(delete_command)
        except exceptions.CommandFailed:
            # This resource was already purged successfully
            pass

    def _create_subnet(self, name, tenant_id, cidr):
        params = ('%(name)s --name %(name)s --tenant-id %(tenant)s '
                  '%(cidr)s' % {'name': name,
                                'tenant': tenant_id,
                                'cidr': cidr})
        subnet = self.parser.listing(self.neutron('subnet-create',
                                                  params=params))
        for row in subnet:
            if row['Field'] == 'id':
                return row['Value']

    def _create_router(self, name, tenant_id):
        params = ('%(name)s --tenant_id %(tenant)s' % {'name': name,
                                                       'tenant': tenant_id})
        router = self.parser.listing(self.neutron('router-create',
                                                  params=params))
        for row in router:
            if row['Field'] == 'id':
                return row['Value']

    def _create_floatingip(self, network, tenant_id):
        params = ('%(network)s --tenant-id %(tenant)s' %
                  {'network': network, 'tenant': tenant_id})
        floatingip = self.parser.listing(self.neutron('floatingip-create',
                                                      params=params))
        for row in floatingip:
            if row['Field'] == 'id':
                return row['Value']

    def _create_resources(self, name, tenant_id, shared_tenant_id=None):
        # If no shared_tenant_id is provided, create the resources for the
        # current tenant to test that they will be deleted when not in use.
        if not shared_tenant_id:
            shared_tenant_id = tenant_id

        self.neutron('net-create',
                     params=('%(name)s --router:external True '
                             '--tenant-id %(tenant)s' % {'name': name,
                                                         'tenant': tenant_id}))
        self.addCleanup(self._safe_cleanup, 'net-delete %s' % name)

        self.neutron('net-create',
                     params=('%(name)s-shared --shared '
                             '--tenant-id %(tenant)s' %
                             {'name': name, 'tenant': shared_tenant_id}))
        self.addCleanup(self._safe_cleanup,
                        'net-delete %s-shared' % name)

        subnet = self._create_subnet(name, tenant_id, '192.168.71.0/24')
        self.addCleanup(self._safe_cleanup, 'subnet-delete %s' % name)

        subnet = self._create_subnet('%s-shared' % name, tenant_id,
                                     '192.168.81.0/24')
        self.addCleanup(self._safe_cleanup, 'subnet-delete %s-shared' % name)

        router = self._create_router(name, tenant_id)
        self.addCleanup(self._safe_cleanup, 'router-delete %s' % name)

        self.neutron('router-interface-add',
                     params=('%(router)s %(subnet)s '
                             '--tenant-id %(tenant)s' % {'router': router,
                                                         'subnet': subnet,
                                                         'tenant': tenant_id}))

        self.neutron('port-create',
                     params=('%(name)s --name %(name)s '
                             '--tenant-id %(tenant)s' % {'name': name,
                                                         'tenant': tenant_id}))
        self.addCleanup(self._safe_cleanup, 'port-delete %s' % name)

        self.neutron('port-create',
                     params=('%(name)s-shared --name %(name)s-shared '
                             '--tenant-id %(tenant)s' % {'name': name,
                                                         'tenant': tenant_id}))
        self.addCleanup(self._safe_cleanup, 'port-delete %s-shared' % name)

        self.neutron('security-group-create',
                     params=('%(name)s --tenant-id %(tenant)s' %
                             {'name': name, 'tenant': tenant_id}))
        self.addCleanup(self._safe_cleanup, 'security-group-delete %s' % name)

        floatingip = self._create_floatingip(name, tenant_id)
        self.addCleanup(self._safe_cleanup, ('floatingip-delete '
                                             '%s' % floatingip))
        return floatingip

    def _verify_deletion(self, resources, resource_type):
        purged = True
        no_purge_purged = True
        router_interface_owners = ['network:router_interface',
                                   'network:router_interface_distributed']
        for row in resources:
            if resource_type == 'port' and row.get('id', None):
                port = self.parser.listing(self.neutron('port-show',
                                                        params=row['id']))
                port_dict = {}
                for row in port:
                    port_dict[row['Field']] = row['Value']
                if port_dict['device_owner'] in router_interface_owners:
                    if port_dict['tenant_id'] == 'purge-tenant':
                        purged = False
                    elif port_dict['tenant_id'] == 'no-purge-tenant':
                        no_purge_purged = False
                    if not purged or not no_purge_purged:
                        self.addCleanup(self.neutron,
                                        ('router-interface-delete %(router)s '
                                         'port=%(port)s' %
                                         {'router': port_dict['device_id'],
                                          'port': port_dict['id']}))
            if (row.get('name') == 'purge-me' or
                    row.get('id') == self.purge_floatingip):
                purged = False
            elif ('no-purge' in row.get('name', '') or
                    row.get('id') == self.no_purge_floatingip):
                no_purge_purged = False

        if not purged:
            self.fail('%s not deleted by neutron purge' % resource_type)

        if no_purge_purged:
            self.fail('%s owned by another tenant incorrectly deleted '
                      'by neutron purge' % resource_type)

    def test_purge(self):
        self.purge_floatingip = self._create_resources('purge-me',
                                                       'purge-tenant')
        self.no_purge_floatingip = self._create_resources('no-purge',
                                                          'no-purge-tenant',
                                                          'purge-tenant')

        purge_output = self.neutron('purge', params='purge-tenant').strip()
        if not purge_output:
            self.fail('Purge command did not return feedback')

        networks = self.parser.listing(self.neutron('net-list'))
        subnets = self.parser.listing(self.neutron('subnet-list'))
        routers = self.parser.listing(self.neutron('router-list'))
        ports = self.parser.listing(self.neutron('port-list'))
        floatingips = self.parser.listing(self.neutron('floatingip-list'))

        self._verify_deletion(networks, 'network')
        self._verify_deletion(subnets, 'subnet')
        self._verify_deletion(ports, 'port')
        self._verify_deletion(routers, 'router')
        self._verify_deletion(floatingips, 'floatingip')
