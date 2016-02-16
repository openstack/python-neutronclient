# Copyright 2013 Big Switch Networks Inc.
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

import sys

from neutronclient.neutron.v2_0.fw import firewallrule
from neutronclient.tests.unit import test_cli20


class CLITestV20FirewallRuleJSON(test_cli20.CLITestV20Base):

    def _test_create_firewall_rule_with_mandatory_params(self, enabled):
        # firewall-rule-create with mandatory (none) params only.
        resource = 'firewall_rule'
        cmd = firewallrule.CreateFirewallRule(test_cli20.MyApp(sys.stdout),
                                              None)
        tenant_id = 'my-tenant'
        name = ''
        my_id = 'myid'
        protocol = 'tcp'
        action = 'allow'
        ip_version = 4
        args = ['--tenant-id', tenant_id,
                '--admin-state-up',
                '--protocol', protocol,
                '--action', action,
                '--enabled', enabled]
        position_names = []
        position_values = []
        self._test_create_resource(resource, cmd, name, my_id, args,
                                   position_names, position_values,
                                   protocol=protocol, action=action,
                                   enabled=enabled, tenant_id=tenant_id,
                                   ip_version=ip_version)

    def test_create_enabled_firewall_rule_with_mandatory_params_lcase(self):
        self._test_create_firewall_rule_with_mandatory_params(enabled='true')

    def test_create_disabled_firewall_rule_with_mandatory_params_lcase(self):
        self._test_create_firewall_rule_with_mandatory_params(enabled='false')

    def test_create_enabled_firewall_rule_with_mandatory_params(self):
        self._test_create_firewall_rule_with_mandatory_params(enabled='True')

    def test_create_disabled_firewall_rule_with_mandatory_params(self):
        self._test_create_firewall_rule_with_mandatory_params(enabled='False')

    def _setup_create_firewall_rule_with_all_params(
            self, protocol='tcp', protocol_cli=None,
            action='allow', action_cli=None, ip_version='4'):
        # firewall-rule-create with all params set.
        resource = 'firewall_rule'
        cmd = firewallrule.CreateFirewallRule(test_cli20.MyApp(sys.stdout),
                                              None)
        name = 'my-name'
        description = 'my-desc'
        source_ip = '192.168.1.0/24'
        destination_ip = '192.168.2.0/24'
        source_port = '0:65535'
        destination_port = '0:65535'
        tenant_id = 'my-tenant'
        my_id = 'myid'
        enabled = 'True'
        args = ['--description', description,
                '--shared',
                '--protocol', protocol_cli or protocol,
                '--ip-version', ip_version,
                '--source-ip-address', source_ip,
                '--destination-ip-address', destination_ip,
                '--source-port', source_port,
                '--destination-port', destination_port,
                '--action', action_cli or action,
                '--enabled', enabled,
                '--admin-state-up',
                '--tenant-id', tenant_id]
        position_names = []
        position_values = []
        if protocol == 'any':
            protocol = None
        if ip_version == '4' or ip_version == '6':
            self._test_create_resource(resource, cmd, name, my_id, args,
                                       position_names, position_values,
                                       description=description, shared=True,
                                       protocol=protocol,
                                       ip_version=int(ip_version),
                                       source_ip_address=source_ip,
                                       destination_ip_address=destination_ip,
                                       source_port=source_port,
                                       destination_port=destination_port,
                                       action=action, enabled='True',
                                       tenant_id=tenant_id)
        else:
            self.assertRaises(SystemExit, self._test_create_resource,
                              resource, cmd, name, my_id, args,
                              position_names, position_values,
                              ip_version=int(ip_version),
                              source_ip_address=source_ip,
                              destination_ip_address=destination_ip,
                              source_port=source_port,
                              destination_port=destination_port,
                              action=action, enabled='True',
                              tenant_id=tenant_id)

    def test_create_firewall_rule_with_all_params(self):
        self._setup_create_firewall_rule_with_all_params()

    def test_create_firewall_rule_with_proto_any(self):
        self._setup_create_firewall_rule_with_all_params(protocol='any')

    def test_create_firewall_rule_with_IP_version_6(self):
        self._setup_create_firewall_rule_with_all_params(ip_version='6')

    def test_create_firewall_rule_with_invalid_IP_version(self):
        self._setup_create_firewall_rule_with_all_params(ip_version='5')

    def test_create_firewall_rule_with_proto_action_upper_capitalized(self):
        for protocol in ('TCP', 'Tcp', 'ANY', 'AnY'):
            self._setup_create_firewall_rule_with_all_params(
                protocol=protocol.lower(),
                protocol_cli=protocol)
        for action in ('Allow', 'DENY', 'reject'):
            self._setup_create_firewall_rule_with_all_params(
                action=action.lower(),
                action_cli=action)

    def test_list_firewall_rules(self):
        # firewall-rule-list.
        resources = "firewall_rules"
        cmd = firewallrule.ListFirewallRule(test_cli20.MyApp(sys.stdout),
                                            None)
        self._test_list_resources(resources, cmd, True)

    def test_list_firewall_rules_pagination(self):
        # firewall-rule-list.
        resources = "firewall_rules"
        cmd = firewallrule.ListFirewallRule(test_cli20.MyApp(sys.stdout),
                                            None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_firewall_rules_sort(self):
        # firewall-rule-list --sort-key name --sort-key id --sort-key asc
        # --sort-key desc
        resources = "firewall_rules"
        cmd = firewallrule.ListFirewallRule(test_cli20.MyApp(sys.stdout),
                                            None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_firewall_rules_limit(self):
        # firewall-rule-list -P."""
        resources = "firewall_rules"
        cmd = firewallrule.ListFirewallRule(test_cli20.MyApp(sys.stdout),
                                            None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_show_firewall_rule_id(self):
        # firewall-rule-show test_id.
        resource = 'firewall_rule'
        cmd = firewallrule.ShowFirewallRule(test_cli20.MyApp(sys.stdout),
                                            None)
        args = ['--fields', 'id', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args, ['id'])

    def test_show_firewall_rule_id_name(self):
        # firewall-rule-show.
        resource = 'firewall_rule'
        cmd = firewallrule.ShowFirewallRule(test_cli20.MyApp(sys.stdout),
                                            None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_update_firewall_rule(self):
        # firewall-rule-update myid --name newname.
        resource = 'firewall_rule'
        cmd = firewallrule.UpdateFirewallRule(test_cli20.MyApp(sys.stdout),
                                              None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'newname'],
                                   {'name': 'newname', })

        # firewall-rule-update myid --protocol any.
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--protocol', 'any'],
                                   {'protocol': None, })

        # firewall-rule-update myid --description any
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--description', 'any'],
                                   {'description': 'any', })

        # firewall-rule-update myid --source_ip_address 192.192.192.192
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--source_ip_address',
                                    '192.192.192.192'],
                                   {'source_ip_address': '192.192.192.192', })

        # firewall-rule-update myid --source_port 32767
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--source_port', '32767'],
                                   {'source_port': '32767', })

        # firewall-rule-update myid --destination_ip_address 0.1.0.1
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--destination_ip_address',
                                    '0.1.0.1'],
                                   {'destination_ip_address': '0.1.0.1', })

        # firewall-rule-update myid --destination_port 65432
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--destination_port',
                                    '65432'],
                                   {'destination_port': '65432', })

        # firewall-rule-update myid --enabled  False
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--enabled', 'False'],
                                   {'enabled': 'False', })

        # firewall-rule-update myid --action reject
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--action', 'reject'],
                                   {'action': 'reject', })

        # firewall-rule-update myid --shared false
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--shared', 'false'],
                                   {'shared': 'false', })

    def test_delete_firewall_rule(self):
        # firewall-rule-delete my-id.
        resource = 'firewall_rule'
        cmd = firewallrule.DeleteFirewallRule(test_cli20.MyApp(sys.stdout),
                                              None)
        my_id = 'myid1'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)
