# Copyright 2012 OpenStack Foundation.
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

import argparse

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


def _get_remote(rule):
    if rule['remote_ip_prefix']:
        remote = '%s (CIDR)' % rule['remote_ip_prefix']
    elif rule['remote_group_id']:
        remote = '%s (group)' % rule['remote_group_id']
    else:
        remote = None
    return remote


def _get_protocol_port(rule):
    proto = rule['protocol']
    port_min = rule['port_range_min']
    port_max = rule['port_range_max']
    if proto in ('tcp', 'udp'):
        if (port_min and port_min == port_max):
            protocol_port = '%s/%s' % (port_min, proto)
        elif port_min:
            protocol_port = '%s-%s/%s' % (port_min, port_max, proto)
        else:
            protocol_port = proto
    elif proto == 'icmp':
        icmp_opts = []
        if port_min is not None:
            icmp_opts.append('type:%s' % port_min)
        if port_max is not None:
            icmp_opts.append('code:%s' % port_max)

        if icmp_opts:
            protocol_port = 'icmp (%s)' % ', '.join(icmp_opts)
        else:
            protocol_port = 'icmp'
    elif proto is not None:
        # port_range_min/max are not recognized for protocol
        # other than TCP, UDP and ICMP.
        protocol_port = proto
    else:
        protocol_port = None

    return protocol_port


def _format_sg_rule(rule):
    formatted = []
    for field in ['direction',
                  'ethertype',
                  ('protocol_port', _get_protocol_port),
                  'remote_ip_prefix',
                  'remote_group_id']:
        if isinstance(field, tuple):
            field, get_method = field
            data = get_method(rule)
        else:
            data = rule[field]
        if not data:
            continue
        if field in ('remote_ip_prefix', 'remote_group_id'):
            data = '%s: %s' % (field, data)
        formatted.append(data)
    return ', '.join(formatted)


def _format_sg_rules(secgroup):
    try:
        return '\n'.join(sorted([_format_sg_rule(rule) for rule
                                 in secgroup['security_group_rules']]))
    except Exception:
        return ''


def generate_default_ethertype(protocol):
    if protocol == 'icmpv6':
        return 'IPv6'
    return 'IPv4'


class ListSecurityGroup(neutronV20.ListCommand):
    """List security groups that belong to a given tenant."""

    resource = 'security_group'
    list_columns = ['id', 'name', 'security_group_rules']
    _formatters = {'security_group_rules': _format_sg_rules}
    pagination_support = True
    sorting_support = True


class ShowSecurityGroup(neutronV20.ShowCommand):
    """Show information of a given security group."""

    resource = 'security_group'
    allow_names = True
    json_indent = 5


class CreateSecurityGroup(neutronV20.CreateCommand):
    """Create a security group."""

    resource = 'security_group'

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help=_('Name of the security group to be created.'))
        parser.add_argument(
            '--description',
            help=_('Description of the security group to be created.'))

    def args2body(self, parsed_args):
        body = {'name': parsed_args.name}
        neutronV20.update_dict(parsed_args, body,
                               ['description', 'tenant_id'])
        return {'security_group': body}


class DeleteSecurityGroup(neutronV20.DeleteCommand):
    """Delete a given security group."""

    resource = 'security_group'
    allow_names = True


class UpdateSecurityGroup(neutronV20.UpdateCommand):
    """Update a given security group."""

    resource = 'security_group'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help=_('Updated name of the security group.'))
        parser.add_argument(
            '--description',
            help=_('Updated description of the security group.'))

    def args2body(self, parsed_args):
        body = {}
        neutronV20.update_dict(parsed_args, body,
                               ['name', 'description'])
        return {'security_group': body}


class ListSecurityGroupRule(neutronV20.ListCommand):
    """List security group rules that belong to a given tenant."""

    resource = 'security_group_rule'
    list_columns = ['id', 'security_group_id', 'direction',
                    'ethertype', 'port/protocol', 'remote']
    # replace_rules: key is an attribute name in Neutron API and
    # corresponding value is a display name shown by CLI.
    replace_rules = {'security_group_id': 'security_group',
                     'remote_group_id': 'remote_group'}
    digest_fields = {
        # The entry 'protocol/port' is left deliberately for backwards
        # compatibility.
        'remote': {
            'method': _get_remote,
            'depends_on': ['remote_ip_prefix', 'remote_group_id']},
        'port/protocol': {
            'method': _get_protocol_port,
            'depends_on': ['protocol', 'port_range_min', 'port_range_max']},
        'protocol/port': {
            'method': _get_protocol_port,
            'depends_on': ['protocol', 'port_range_min', 'port_range_max']}}
    pagination_support = True
    sorting_support = True

    def get_parser(self, prog_name):
        parser = super(ListSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            '--no-nameconv', action='store_true',
            help=_('Do not convert security group ID to its name.'))
        return parser

    @staticmethod
    def replace_columns(cols, rules, reverse=False):
        if reverse:
            rules = dict((rules[k], k) for k in rules.keys())
        return [rules.get(col, col) for col in cols]

    def get_required_fields(self, fields):
        fields = self.replace_columns(fields, self.replace_rules, reverse=True)
        for field, digest_fields in self.digest_fields.items():
            if field in fields:
                fields += digest_fields['depends_on']
                fields.remove(field)
        return fields

    def retrieve_list(self, parsed_args):
        parsed_args.fields = self.get_required_fields(parsed_args.fields)
        return super(ListSecurityGroupRule, self).retrieve_list(parsed_args)

    def _get_sg_name_dict(self, data, page_size, no_nameconv):
        """Get names of security groups referred in the retrieved rules.

        :return: a dict from secgroup ID to secgroup name
        """
        if no_nameconv:
            return {}
        neutron_client = self.get_client()
        search_opts = {'fields': ['id', 'name']}
        if self.pagination_support:
            if page_size:
                search_opts.update({'limit': page_size})
        sec_group_ids = set()
        for rule in data:
            for key in self.replace_rules:
                if rule.get(key):
                    sec_group_ids.add(rule[key])
        sec_group_ids = list(sec_group_ids)

        def _get_sec_group_list(sec_group_ids):
            search_opts['id'] = sec_group_ids
            return neutron_client.list_security_groups(
                **search_opts).get('security_groups', [])

        try:
            secgroups = _get_sec_group_list(sec_group_ids)
        except exceptions.RequestURITooLong as uri_len_exc:
            # Length of a query filter on security group rule id
            # id=<uuid>& (with len(uuid)=36)
            sec_group_id_filter_len = 40
            # The URI is too long because of too many sec_group_id filters
            # Use the excess attribute of the exception to know how many
            # sec_group_id filters can be inserted into a single request
            sec_group_count = len(sec_group_ids)
            max_size = ((sec_group_id_filter_len * sec_group_count) -
                        uri_len_exc.excess)
            chunk_size = max_size // sec_group_id_filter_len
            secgroups = []
            for i in range(0, sec_group_count, chunk_size):
                secgroups.extend(
                    _get_sec_group_list(sec_group_ids[i: i + chunk_size]))

        return dict([(sg['id'], sg['name'])
                     for sg in secgroups if sg['name']])

    @staticmethod
    def _has_fields(rule, required_fields):
        return all([key in rule for key in required_fields])

    def extend_list(self, data, parsed_args):
        sg_dict = self._get_sg_name_dict(data, parsed_args.page_size,
                                         parsed_args.no_nameconv)
        for rule in data:
            # Replace security group UUID with its name.
            for key in self.replace_rules:
                if key in rule:
                    rule[key] = sg_dict.get(rule[key], rule[key])
            for field, digest_rule in self.digest_fields.items():
                if self._has_fields(rule, digest_rule['depends_on']):
                    rule[field] = digest_rule['method'](rule) or 'any'

    def setup_columns(self, info, parsed_args):
        # Translate the specified columns from the command line
        # into field names used in "info".
        parsed_args.columns = self.replace_columns(parsed_args.columns,
                                                   self.replace_rules,
                                                   reverse=True)
        # NOTE(amotoki): 2nd element of the tuple returned by setup_columns()
        # is a generator, so if you need to create a look using the generator
        # object, you need to recreate a generator to show a list expectedly.
        info = super(ListSecurityGroupRule, self).setup_columns(info,
                                                                parsed_args)
        cols = info[0]
        if not parsed_args.no_nameconv:
            # Replace column names in the header line (in info[0])
            cols = self.replace_columns(info[0], self.replace_rules)
            parsed_args.columns = cols
        return (cols, info[1])


class ShowSecurityGroupRule(neutronV20.ShowCommand):
    """Show information of a given security group rule."""

    resource = 'security_group_rule'
    allow_names = False


class CreateSecurityGroupRule(neutronV20.CreateCommand):
    """Create a security group rule."""

    resource = 'security_group_rule'

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            help=_('Description of security group rule.'))
        parser.add_argument(
            'security_group_id', metavar='SECURITY_GROUP',
            help=_('ID or name of the security group to '
                   'which the rule is added.'))
        parser.add_argument(
            '--direction',
            type=utils.convert_to_lowercase,
            default='ingress', choices=['ingress', 'egress'],
            help=_('Direction of traffic: ingress/egress.'))
        parser.add_argument(
            '--ethertype',
            help=_('IPv4/IPv6'))
        parser.add_argument(
            '--protocol',
            type=utils.convert_to_lowercase,
            help=_('Protocol of packet. Allowed values are '
                   '[icmp, icmpv6, tcp, udp] and '
                   'integer representations [0-255].'))
        parser.add_argument(
            '--port-range-min',
            help=_('Starting port range. For ICMP it is type.'))
        parser.add_argument(
            '--port_range_min',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--port-range-max',
            help=_('Ending port range. For ICMP it is code.'))
        parser.add_argument(
            '--port_range_max',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--remote-ip-prefix',
            help=_('CIDR to match on.'))
        parser.add_argument(
            '--remote_ip_prefix',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--remote-group-id', metavar='REMOTE_GROUP',
            help=_('ID or name of the remote security group '
                   'to which the rule is applied.'))
        parser.add_argument(
            '--remote_group_id',
            help=argparse.SUPPRESS)

    def args2body(self, parsed_args):
        _security_group_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'security_group', parsed_args.security_group_id)
        body = {'security_group_id': _security_group_id,
                'direction': parsed_args.direction,
                'ethertype': parsed_args.ethertype or
                generate_default_ethertype(parsed_args.protocol)}
        neutronV20.update_dict(parsed_args, body,
                               ['protocol', 'port_range_min', 'port_range_max',
                                'remote_ip_prefix', 'tenant_id',
                                'description'])
        if parsed_args.remote_group_id:
            _remote_group_id = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'security_group',
                parsed_args.remote_group_id)
            body['remote_group_id'] = _remote_group_id
        return {'security_group_rule': body}


class DeleteSecurityGroupRule(neutronV20.DeleteCommand):
    """Delete a given security group rule."""

    resource = 'security_group_rule'
    allow_names = False
