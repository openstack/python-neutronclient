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

import itertools
import sys

import mock
from oslo_serialization import jsonutils

from neutronclient.common import exceptions
from neutronclient.neutron.v2_0 import network
from neutronclient import shell
from neutronclient.tests.unit import test_cli20


class CLITestV20CreateNetworkJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        super(CLITestV20CreateNetworkJSON, self).setUp(plurals={'tags': 'tag'})

    def _test_create_network(self, **kwargs):
        cmd = network.CreateNetwork(test_cli20.MyApp(sys.stdout), None)
        resource = kwargs.pop('resource', 'network')

        name = kwargs.pop('name', 'myname')
        myid = kwargs.pop('myid', 'myid')
        args = kwargs.pop('args', [name, ])
        position_names = kwargs.pop('position_names', ['name', ])
        position_values = kwargs.pop('position_values', [name, ])

        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   **kwargs)

    def test_create_network(self):
        # Create net: myname.
        self._test_create_network()

    def test_create_network_with_unicode(self):
        # Create net: u'\u7f51\u7edc'.
        self._test_create_network(name=u'\u7f51\u7edc')

    def test_create_network_description(self):
        # Create net: --tenant_id tenantid myname.
        name = 'myname'
        args = ['--description', 'Nice network', name]
        self._test_create_network(name=name,
                                  args=args,
                                  description='Nice network')

    def test_create_network_tenant_underscore(self):
        # Create net: --tenant_id tenantid myname.
        name = 'myname'
        args = ['--tenant_id', 'tenantid', name]
        self._test_create_network(name=name, args=args, tenant_id="tenantid")

    def test_create_network_tenant_dash(self):
        # Test dashed options
        # Create net: --tenant_id tenantid myname.
        name = 'myname'
        args = ['--tenant-id', 'tenantid', name]
        self._test_create_network(name=name, args=args, tenant_id="tenantid")

    def test_create_network_provider_args(self):
        # Create net: with --provider arguments.
        # Test --provider attributes before network name
        name = 'myname'
        args = ['--provider:network_type', 'vlan',
                '--provider:physical_network', 'physnet1',
                '--provider:segmentation_id', '400', name]
        position_names = ['provider:network_type',
                          'provider:physical_network',
                          'provider:segmentation_id', 'name']
        position_values = ['vlan', 'physnet1', '400', name]
        self._test_create_network(name=name,
                                  args=args,
                                  position_names=position_names,
                                  position_values=position_values)

    def test_create_network_tags(self):
        # Create net: myname --tags a b.
        name = 'myname'
        args = [name, '--tags', 'a', 'b']
        self._test_create_network(name=name, args=args, tags=['a', 'b'])

    def test_create_network_state_underscore(self):
        # Create net: --admin_state_down myname.
        name = 'myname'
        args = ['--admin_state_down', name, ]
        self._test_create_network(name=name, args=args, admin_state_up=False)

    def test_create_network_state_dash(self):
        # Test dashed options
        name = 'myname'
        args = ['--admin-state-down', name, ]
        self._test_create_network(name=name, args=args, admin_state_up=False)

    def test_create_network_vlan_transparent(self):
        # Create net: myname --vlan-transparent True.
        name = 'myname'
        args = ['--vlan-transparent', 'True', name]
        self._test_create_network(name=name,
                                  args=args,
                                  vlan_transparent='True')

    def test_create_network_with_qos_policy(self):
        # Create net: --qos-policy mypolicy.
        name = 'myname'
        qos_policy_name = 'mypolicy'
        args = [name, '--qos-policy', qos_policy_name]
        position_names = ['name', 'qos_policy_id']
        position_values = [name, qos_policy_name]
        self._test_create_network(name=name,
                                  args=args,
                                  position_names=position_names,
                                  position_values=position_values)

    def test_create_network_with_az_hint(self):
        # Create net: --availability-zone-hint zone1
        # --availability-zone-hint zone2.
        name = 'myname'
        args = ['--availability-zone-hint', 'zone1',
                '--availability-zone-hint', 'zone2', name]
        position_names = ['availability_zone_hints', 'name']
        position_values = [['zone1', 'zone2'], name]
        self._test_create_network(name=name,
                                  args=args,
                                  position_names=position_names,
                                  position_values=position_values)

    def test_create_network_with_dns_domain(self):
        # Create net: --dns-domain my-domain.org.
        name = 'myname'
        dns_domain_name = 'my-domain.org.'
        args = [name, '--dns-domain', dns_domain_name]
        position_names = ['name', 'dns_domain']
        position_values = [name, dns_domain_name]
        self._test_create_network(name=name,
                                  args=args,
                                  position_names=position_names,
                                  position_values=position_values)


class CLITestV20ListNetworkJSON(test_cli20.CLITestV20Base):
    def setUp(self):
        super(CLITestV20ListNetworkJSON, self).setUp(plurals={'tags': 'tag'})

    def test_list_nets_empty_with_column(self):
        resources = "networks"
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        reses = {resources: []}
        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)
        # url method body
        query = "id=myfakeid"
        args = ['-c', 'id', '--', '--id', 'myfakeid']
        path = getattr(self.client, resources + "_path")
        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request, \
                mock.patch.object(network.ListNetwork, "extend_list",
                                  return_value=None) as mock_extend_list:
            cmd_parser = cmd.get_parser("list_" + resources)
            shell.run_command(cmd, cmd_parser, args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(test_cli20.end_url(path, query),
                                       self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)
        _str = self.fake_stdout.make_string()
        self.assertEqual('\n', _str)

    def _test_list_networks(self, cmd, detail=False, tags=(),
                            fields_1=(), fields_2=(), page_size=None,
                            sort_key=(), sort_dir=(), base_args=None,
                            query=''):
        resources = "networks"
        with mock.patch.object(network.ListNetwork, "extend_list",
                               return_value=None) as mock_extend_list:
            self._test_list_resources(resources, cmd, detail, tags,
                                      fields_1, fields_2, page_size=page_size,
                                      sort_key=sort_key, sort_dir=sort_dir,
                                      base_args=base_args, query=query)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def test_list_nets_pagination(self):
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        with mock.patch.object(network.ListNetwork, "extend_list",
                               return_value=None) as mock_extend_list:
            self._test_list_resources_with_pagination("networks", cmd)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def test_list_nets_sort(self):
        # list nets:
        # --sort-key name --sort-key id --sort-dir asc --sort-dir desc
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, sort_key=['name', 'id'],
                                 sort_dir=['asc', 'desc'])

    def test_list_nets_sort_with_keys_more_than_dirs(self):
        # list nets: --sort-key name --sort-key id --sort-dir desc
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, sort_key=['name', 'id'],
                                 sort_dir=['desc'])

    def test_list_nets_sort_with_dirs_more_than_keys(self):
        # list nets: --sort-key name --sort-dir desc --sort-dir asc
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, sort_key=['name'],
                                 sort_dir=['desc', 'asc'])

    def test_list_nets_limit(self):
        # list nets: -P.
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, page_size=1000)

    def test_list_nets_detail(self):
        # list nets: -D.
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, True)

    def test_list_nets_tags(self):
        # List nets: -- --tags a b.
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, tags=['a', 'b'])

    def test_list_nets_tags_with_unicode(self):
        # List nets: -- --tags u'\u7f51\u7edc'.
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, tags=[u'\u7f51\u7edc'])

    def test_list_nets_detail_tags(self):
        # List nets: -D -- --tags a b.
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, detail=True, tags=['a', 'b'])

    def _test_list_nets_extend_subnets(self, data, expected):
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        nets_path = getattr(self.client, 'networks_path')
        subnets_path = getattr(self.client, 'subnets_path')
        nets_query = ''
        filters = ''
        for n in data:
            for s in n['subnets']:
                filters = filters + "&id=%s" % s
        subnets_query = 'fields=id&fields=cidr' + filters
        with mock.patch.object(cmd, 'get_client',
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient,
                                  "request") as mock_request:
            resp1 = (test_cli20.MyResp(200),
                     self.client.serialize({'networks': data}))
            resp2 = (test_cli20.MyResp(200),
                     self.client.serialize({'subnets': [
                         {'id': 'mysubid1', 'cidr': '192.168.1.0/24'},
                         {'id': 'mysubid2', 'cidr': '172.16.0.0/24'},
                         {'id': 'mysubid3', 'cidr': '10.1.1.0/24'}]}))
            mock_request.side_effect = [resp1, resp2]
            args = []
            cmd_parser = cmd.get_parser('list_networks')
            parsed_args = cmd_parser.parse_args(args)
            result = cmd.take_action(parsed_args)

        mock_get_client.assert_called_with()
        self.assertEqual(2, mock_request.call_count)
        mock_request.assert_has_calls([
            mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(nets_path, nets_query),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN})),
            mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(subnets_path, subnets_query),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN}))])
        _result = [x for x in result[1]]
        self.assertEqual(len(expected), len(_result))
        for res, exp in zip(_result, expected):
            self.assertEqual(len(exp), len(res))
            for obsrvd, expctd in zip(res, exp):
                self.assertEqual(expctd, obsrvd)

    def test_list_nets_extend_subnets(self):
        data = [{'id': 'netid1', 'name': 'net1', 'subnets': ['mysubid1']},
                {'id': 'netid2', 'name': 'net2', 'subnets': ['mysubid2',
                                                             'mysubid3']}]
        #             id,   name,   subnets
        expected = [('netid1', 'net1', 'mysubid1 192.168.1.0/24'),
                    ('netid2', 'net2',
                     'mysubid2 172.16.0.0/24\nmysubid3 10.1.1.0/24')]
        self._test_list_nets_extend_subnets(data, expected)

    def test_list_nets_extend_subnets_no_subnet(self):
        data = [{'id': 'netid1', 'name': 'net1', 'subnets': ['mysubid1']},
                {'id': 'netid2', 'name': 'net2', 'subnets': ['mysubid4']}]
        #             id,   name,   subnets
        expected = [('netid1', 'net1', 'mysubid1 192.168.1.0/24'),
                    ('netid2', 'net2', 'mysubid4 ')]
        self._test_list_nets_extend_subnets(data, expected)

    def test_list_nets_fields(self):
        # List nets: --fields a --fields b -- --fields c d.
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd,
                                 fields_1=['a', 'b'], fields_2=['c', 'd'])

    def _test_list_nets_columns(self, cmd, returned_body,
                                args=('-f', 'json')):
        resources = 'networks'
        with mock.patch.object(network.ListNetwork, "extend_list",
                               return_value=None) as mock_extend_list:
            self._test_list_columns(cmd, resources, returned_body, args=args)
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)

    def test_list_nets_defined_column(self):
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        returned_body = {"networks": [{"name": "buildname3",
                                       "id": "id3",
                                       "tenant_id": "tenant_3",
                                       "subnets": []}]}
        self._test_list_nets_columns(cmd, returned_body,
                                     args=['-f', 'json', '-c', 'id'])
        _str = self.fake_stdout.make_string()
        returned_networks = jsonutils.loads(_str)
        self.assertEqual(1, len(returned_networks))
        net = returned_networks[0]
        self.assertEqual(1, len(net))
        self.assertIn("id", net.keys())

    def test_list_nets_with_default_column(self):
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        returned_body = {"networks": [{"name": "buildname3",
                                       "id": "id3",
                                       "tenant_id": "tenant_3",
                                       "subnets": []}]}
        self._test_list_nets_columns(cmd, returned_body)
        _str = self.fake_stdout.make_string()
        returned_networks = jsonutils.loads(_str)
        self.assertEqual(1, len(returned_networks))
        net = returned_networks[0]
        self.assertEqual(3, len(net))
        self.assertEqual(0, len(set(net) ^ set(cmd.list_columns)))

    def test_list_external_nets_empty_with_column(self):
        resources = "networks"
        cmd = network.ListExternalNetwork(test_cli20.MyApp(sys.stdout), None)
        reses = {resources: []}
        resstr = self.client.serialize(reses)
        # url method body
        query = "router%3Aexternal=True&id=myfakeid"
        args = ['-c', 'id', '--', '--id', 'myfakeid']
        path = getattr(self.client, resources + "_path")
        resp = (test_cli20.MyResp(200), resstr)
        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request, \
                mock.patch.object(network.ListNetwork, "extend_list",
                                  return_value=None) as mock_extend_list:
            cmd_parser = cmd.get_parser("list_" + resources)
            shell.run_command(cmd, cmd_parser, args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, query), self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)
        _str = self.fake_stdout.make_string()
        self.assertEqual('\n', _str)

    def _test_list_external_nets(self, resources, cmd,
                                 detail=False, tags=(),
                                 fields_1=(), fields_2=()):
        reses = {resources: [{'id': 'myid1', },
                             {'id': 'myid2', }, ], }

        resstr = self.client.serialize(reses)
        resp = (test_cli20.MyResp(200), resstr)

        # url method body
        query = ""
        args = detail and ['-D', ] or []
        if fields_1:
            for field in fields_1:
                args.append('--fields')
                args.append(field)
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
        for field in itertools.chain(fields_1, fields_2):
            if query:
                query += "&fields=" + field
            else:
                query = "fields=" + field
        if query:
            query += '&router%3Aexternal=True'
        else:
            query += 'router%3Aexternal=True'
        for tag in tags:
            if query:
                query += "&tag=" + tag
            else:
                query = "tag=" + tag
        if detail:
            query = query and query + '&verbose=True' or 'verbose=True'
        path = getattr(self.client, resources + "_path")

        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=resp) as mock_request, \
                mock.patch.object(network.ListNetwork, "extend_list",
                                  return_value=None) as mock_extend_list:
            cmd_parser = cmd.get_parser("list_" + resources)
            shell.run_command(cmd, cmd_parser, args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(
                test_cli20.end_url(path, query), self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))
        mock_extend_list.assert_called_once_with(test_cli20.IsA(list),
                                                 mock.ANY)
        _str = self.fake_stdout.make_string()

        self.assertIn('myid1', _str)

    def test_list_external_nets_detail(self):
        # list external nets: -D.
        resources = "networks"
        cmd = network.ListExternalNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_external_nets(resources, cmd, True)

    def test_list_external_nets_tags(self):
        # List external nets: -- --tags a b.
        resources = "networks"
        cmd = network.ListExternalNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_external_nets(resources,
                                      cmd, tags=['a', 'b'])

    def test_list_external_nets_detail_tags(self):
        # List external nets: -D -- --tags a b.
        resources = "networks"
        cmd = network.ListExternalNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_external_nets(resources, cmd,
                                      detail=True, tags=['a', 'b'])

    def test_list_external_nets_fields(self):
        # List external nets: --fields a --fields b -- --fields c d.
        resources = "networks"
        cmd = network.ListExternalNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_external_nets(resources, cmd,
                                      fields_1=['a', 'b'],
                                      fields_2=['c', 'd'])

    def test_list_shared_networks(self):
        # list nets : --shared False
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_list_networks(cmd, base_args='--shared False'.split(),
                                 query='shared=False')


class CLITestV20UpdateNetworkJSON(test_cli20.CLITestV20Base):
    def test_update_network_exception(self):
        # Update net: myid.
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_update_network(self):
        # Update net: myid --name myname --tags a b.
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b', '--description',
                                    'This network takes the scenic route'],
                                   {'name': 'myname', 'tags': ['a', 'b'],
                                    'description': 'This network takes the '
                                                   'scenic route'})

    def test_update_network_with_unicode(self):
        # Update net: myid --name u'\u7f51\u7edc' --tags a b.
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', u'\u7f51\u7edc',
                                    '--tags', 'a', 'b'],
                                   {'name': u'\u7f51\u7edc',
                                    'tags': ['a', 'b'], }
                                   )

    def test_update_network_with_qos_policy(self):
        # Update net: myid --qos-policy mypolicy.
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--qos-policy', 'mypolicy'],
                                   {'qos_policy_id': 'mypolicy', })

    def test_update_network_with_no_qos_policy(self):
        # Update net: myid --no-qos-policy.
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--no-qos-policy'],
                                   {'qos_policy_id': None, })

    def test_update_network_with_dns_domain(self):
        # Update net: myid --dns-domain my-domain.org.
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--dns-domain', 'my-domain.org.'],
                                   {'dns_domain': 'my-domain.org.', })

    def test_update_network_with_no_dns_domain(self):
        # Update net: myid --no-dns-domain
        resource = 'network'
        cmd = network.UpdateNetwork(test_cli20.MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--no-dns-domain'],
                                   {'dns_domain': "", })


class CLITestV20ShowNetworkJSON(test_cli20.CLITestV20Base):
    def test_show_network(self):
        # Show net: --fields id --fields name myid.
        resource = 'network'
        cmd = network.ShowNetwork(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])


class CLITestV20DeleteNetworkJSON(test_cli20.CLITestV20Base):
    def test_delete_network(self):
        # Delete net: myid.
        resource = 'network'
        cmd = network.DeleteNetwork(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)

    def test_bulk_delete_network(self):
        # Delete net: myid1 myid2.
        resource = 'network'
        cmd = network.DeleteNetwork(test_cli20.MyApp(sys.stdout), None)
        myid1 = 'myid1'
        myid2 = 'myid2'
        args = [myid1, myid2]
        self._test_delete_resource(resource, cmd, myid1, args, extra_id=myid2)

    def test_bulk_delete_network_fail(self):
        # Delete net: myid1 myid2.
        resource = 'network'
        cmd = network.DeleteNetwork(test_cli20.MyApp(sys.stdout), None)
        myid1 = 'myid1'
        myid2 = 'myid2'
        args = [myid1, myid2]
        self.assertRaises(exceptions.NeutronCLIError,
                          self._test_delete_resource,
                          resource, cmd, myid1, args, extra_id=myid2,
                          delete_fail=True)


class CLITestV20ExtendListNetworkJSON(test_cli20.CLITestV20Base):
    def _build_test_data(self, data):
        subnet_ids = []
        response = []
        filters = ""
        for n in data:
            if 'subnets' in n:
                subnet_ids.extend(n['subnets'])
                for subnet_id in n['subnets']:
                    filters = "%s&id=%s" % (filters, subnet_id)
                    response.append({'id': subnet_id,
                                     'cidr': '192.168.0.0/16'})
        resp_str = self.client.serialize({'subnets': response})
        resp = (test_cli20.MyResp(200), resp_str)
        return filters, resp

    def test_extend_list(self):
        data = [{'id': 'netid%d' % i, 'name': 'net%d' % i,
                 'subnets': ['mysubid%d' % i]}
                for i in range(10)]
        filters, response = self._build_test_data(data)
        path = getattr(self.client, 'subnets_path')
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient, "request",
                                  return_value=response) as mock_request:
            known_args, _vs = cmd.get_parser('create_subnets')\
                .parse_known_args()
            cmd.extend_list(data, known_args)

        mock_get_client.assert_called_once_with()
        mock_request.assert_called_once_with(
            test_cli20.MyUrlComparator(test_cli20.end_url(
                path, 'fields=id&fields=cidr' + filters), self.client),
            'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                {'X-Auth-Token': test_cli20.TOKEN}))

    def test_extend_list_exceed_max_uri_len(self):
        data = [{'id': 'netid%d' % i, 'name': 'net%d' % i,
                 'subnets': ['mysubid%d' % i]}
                for i in range(10)]
        filters1, response1 = self._build_test_data(data[:len(data) - 1])
        filters2, response2 = self._build_test_data(data[len(data) - 1:])
        path = getattr(self.client, 'subnets_path')
        cmd = network.ListNetwork(test_cli20.MyApp(sys.stdout), None)
        with mock.patch.object(cmd, "get_client",
                               return_value=self.client) as mock_get_client, \
                mock.patch.object(self.client.httpclient,
                                  "request") as mock_request, \
                mock.patch.object(self.client.httpclient, "_check_uri_length",
                                  return_value=None) as mock_check_uri_length:
            # 1 char of extra URI len will cause a split in 2 requests
            mock_check_uri_length.side_effect = [
                exceptions.RequestURITooLong(excess=1), None, None]
            mock_request.side_effect = [response1, response2]
            known_args, _vs = cmd.get_parser('create_subnets')\
                .parse_known_args()
            cmd.extend_list(data, known_args)

        mock_get_client.assert_called_once_with()
        self.assertEqual(2, mock_request.call_count)
        mock_request.assert_has_calls([
            mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(
                        path, 'fields=id&fields=cidr%s' % filters1),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN})),
            mock.call(
                test_cli20.MyUrlComparator(
                    test_cli20.end_url(
                        path, 'fields=id&fields=cidr%s' % filters2),
                    self.client),
                'GET',
                body=None,
                headers=test_cli20.ContainsKeyValue(
                    {'X-Auth-Token': test_cli20.TOKEN}))])
