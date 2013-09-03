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

import sys

import mox

from neutronclient.neutron.v2_0 import port
from neutronclient import shell
from neutronclient.tests.unit import test_cli20


class CLITestV20PortJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        super(CLITestV20PortJSON, self).setUp(plurals={'tags': 'tag'})

    def test_create_port(self):
        """Create port: netid."""
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = [netid]
        position_names = ['network_id']
        position_values = []
        position_values.extend([netid])
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_port_full(self):
        """Create port: --mac_address mac --device_id deviceid netid."""
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--mac_address', 'mac', '--device_id', 'deviceid', netid]
        position_names = ['network_id', 'mac_address', 'device_id']
        position_values = [netid, 'mac', 'deviceid']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

        # Test dashed options
        args = ['--mac-address', 'mac', '--device-id', 'deviceid', netid]
        position_names = ['network_id', 'mac_address', 'device_id']
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_port_tenant(self):
        """Create port: --tenant_id tenantid netid."""
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--tenant_id', 'tenantid', netid, ]
        position_names = ['network_id']
        position_values = []
        position_values.extend([netid])
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

        # Test dashed options
        args = ['--tenant-id', 'tenantid', netid, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_port_tags(self):
        """Create port: netid mac_address device_id --tags a b."""
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = [netid, '--tags', 'a', 'b']
        position_names = ['network_id']
        position_values = []
        position_values.extend([netid])
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tags=['a', 'b'])

    def test_create_port_secgroup(self):
        """Create port: --security-group sg1_id netid."""
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--security-group', 'sg1_id', netid]
        position_names = ['network_id', 'security_groups']
        position_values = [netid, ['sg1_id']]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_port_secgroups(self):
        """Create port: <security_groups> netid

        The <security_groups> are
        --security-group sg1_id --security-group sg2_id
        """
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--security-group', 'sg1_id',
                '--security-group', 'sg2_id',
                netid]
        position_names = ['network_id', 'security_groups']
        position_values = [netid, ['sg1_id', 'sg2_id']]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_port_secgroup_off(self):
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--no-security-group', netid]
        position_names = ['network_id', 'security_groups']
        position_values = [netid, None]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_port_secgroups_list(self):
        """Create port: netid <security_groups>
        The <security_groups> are
        --security-groups list=true sg_id1 sg_id2
        """
        resource = 'port'
        cmd = port.CreatePort(test_cli20.MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = [netid, '--security-groups', 'list=true', 'sg_id1', 'sg_id2']
        position_names = ['network_id', 'security_groups']
        position_values = [netid, ['sg_id1', 'sg_id2']]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_list_ports(self):
        """List ports: -D."""
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_ports_pagination(self):
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_ports_sort(self):
        """list ports: --sort-key name --sort-key id --sort-key asc
        --sort-key desc
        """
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_ports_limit(self):
        """list ports: -P."""
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_list_ports_tags(self):
        """List ports: -- --tags a b."""
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_ports_detail_tags(self):
        """List ports: -D -- --tags a b."""
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_ports_fields(self):
        """List ports: --fields a --fields b -- --fields c d."""
        resources = "ports"
        cmd = port.ListPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def _test_list_router_port(self, resources, cmd,
                               myid, detail=False, tags=[],
                               fields_1=[], fields_2=[]):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        reses = {resources: [{'id': 'myid1', },
                             {'id': 'myid2', }, ], }

        resstr = self.client.serialize(reses)

        # url method body
        query = ""
        args = detail and ['-D', ] or []

        if fields_1:
            for field in fields_1:
                args.append('--fields')
                args.append(field)
        args.append(myid)
        if tags:
            args.append('--')
            args.append("--tag")
        for tag in tags:
            args.append(tag)
        if (not tags) and fields_2:
            args.append('--')
        if fields_2:
            args.append("--fields")
            for field in fields_2:
                args.append(field)
        fields_1.extend(fields_2)
        for field in fields_1:
            if query:
                query += "&fields=" + field
            else:
                query = "fields=" + field

        for tag in tags:
            if query:
                query += "&tag=" + tag
            else:
                query = "tag=" + tag
        if detail:
            query = query and query + '&verbose=True' or 'verbose=True'
        query = query and query + '&device_id=%s' or 'device_id=%s'
        path = getattr(self.client, resources + "_path")
        self.client.httpclient.request(
            test_cli20.end_url(path, query % myid), 'GET',
            body=None,
            headers=mox.ContainsKeyValue('X-Auth-Token', test_cli20.TOKEN)
        ).AndReturn((test_cli20.MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()

        self.assertTrue('myid1' in _str)

    def test_list_router_ports(self):
        """List router ports: -D."""
        resources = "ports"
        cmd = port.ListRouterPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_router_port(resources, cmd,
                                    self.test_id, True)

    def test_list_router_ports_tags(self):
        """List router ports: -- --tags a b."""
        resources = "ports"
        cmd = port.ListRouterPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_router_port(resources, cmd,
                                    self.test_id, tags=['a', 'b'])

    def test_list_router_ports_detail_tags(self):
        """List router ports: -D -- --tags a b."""
        resources = "ports"
        cmd = port.ListRouterPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_router_port(resources, cmd, self.test_id,
                                    detail=True, tags=['a', 'b'])

    def test_list_router_ports_fields(self):
        """List ports: --fields a --fields b -- --fields c d."""
        resources = "ports"
        cmd = port.ListRouterPort(test_cli20.MyApp(sys.stdout), None)
        self._test_list_router_port(resources, cmd, self.test_id,
                                    fields_1=['a', 'b'],
                                    fields_2=['c', 'd'])

    def test_update_port(self):
        """Update port: myid --name myname --tags a b."""
        resource = 'port'
        cmd = port.UpdatePort(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_update_port_secgroup(self):
        resource = 'port'
        cmd = port.UpdatePort(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = ['--security-group', 'sg1_id', myid]
        updatefields = {'security_groups': ['sg1_id']}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_port_secgroups(self):
        resource = 'port'
        cmd = port.UpdatePort(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = ['--security-group', 'sg1_id',
                '--security-group', 'sg2_id',
                myid]
        updatefields = {'security_groups': ['sg1_id', 'sg2_id']}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_port_security_group_off(self):
        """Update port: --no-security-groups myid."""
        resource = 'port'
        cmd = port.UpdatePort(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['--no-security-groups', 'myid'],
                                   {'security_groups': None})

    def test_show_port(self):
        """Show port: --fields id --fields name myid."""
        resource = 'port'
        cmd = port.ShowPort(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_delete_port(self):
        """Delete port: myid."""
        resource = 'port'
        cmd = port.DeletePort(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)


class CLITestV20PortXML(CLITestV20PortJSON):
    format = 'xml'
