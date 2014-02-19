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
import logging

from cliff import lister
from cliff import show

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


def get_tenant_id(tenant_id, client):
    return (tenant_id if tenant_id else
            client.get_quotas_tenant()['tenant']['tenant_id'])


class DeleteQuota(neutronV20.NeutronCommand):
    """Delete defined quotas of a given tenant."""

    api = 'network'
    resource = 'quota'
    log = logging.getLogger(__name__ + '.DeleteQuota')

    def get_parser(self, prog_name):
        parser = super(DeleteQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  neutron_client)
        obj_deleter = getattr(neutron_client,
                              "delete_%s" % self.resource)
        obj_deleter(tenant_id)
        print >>self.app.stdout, (_('Deleted %(resource)s: %(tenant_id)s')
                                  % {'tenant_id': tenant_id,
                                     'resource': self.resource})
        return


class ListQuota(neutronV20.NeutronCommand, lister.Lister):
    """List quotas of all tenants who have non-default quota values."""

    api = 'network'
    resource = 'quota'
    log = logging.getLogger(__name__ + '.ListQuota')

    def get_parser(self, prog_name):
        parser = super(ListQuota, self).get_parser(prog_name)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)', parsed_args)
        neutron_client = self.get_client()
        search_opts = {}
        self.log.debug('search options: %s', search_opts)
        neutron_client.format = parsed_args.request_format
        obj_lister = getattr(neutron_client,
                             "list_%ss" % self.resource)
        data = obj_lister(**search_opts)
        info = []
        collection = self.resource + "s"
        if collection in data:
            info = data[collection]
        _columns = len(info) > 0 and sorted(info[0].keys()) or []
        return (_columns, (utils.get_item_properties(s, _columns)
                for s in info))


class ShowQuota(neutronV20.NeutronCommand, show.ShowOne):
    """Show quotas of a given tenant

    """
    api = 'network'
    resource = "quota"
    log = logging.getLogger(__name__ + '.ShowQuota')

    def get_parser(self, prog_name):
        parser = super(ShowQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)', parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  neutron_client)
        params = {}
        obj_shower = getattr(neutron_client,
                             "show_%s" % self.resource)
        data = obj_shower(tenant_id, **params)
        if self.resource in data:
            for k, v in data[self.resource].iteritems():
                if isinstance(v, list):
                    value = ""
                    for _item in v:
                        if value:
                            value += "\n"
                        if isinstance(_item, dict):
                            value += utils.dumps(_item)
                        else:
                            value += str(_item)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''
            return zip(*sorted(data[self.resource].iteritems()))
        else:
            return None


class UpdateQuota(neutronV20.NeutronCommand, show.ShowOne):
    """Define tenant's quotas not to use defaults."""

    resource = 'quota'
    log = logging.getLogger(__name__ + '.UpdateQuota')

    def get_parser(self, prog_name):
        parser = super(UpdateQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--network', metavar='networks',
            help=_('The limit of networks'))
        parser.add_argument(
            '--subnet', metavar='subnets',
            help=_('The limit of subnets'))
        parser.add_argument(
            '--port', metavar='ports',
            help=_('The limit of ports'))
        parser.add_argument(
            '--router', metavar='routers',
            help=_('The limit of routers'))
        parser.add_argument(
            '--floatingip', metavar='floatingips',
            help=_('The limit of floating IPs'))
        parser.add_argument(
            '--security-group', metavar='security_groups',
            help=_('The limit of security groups'))
        parser.add_argument(
            '--security-group-rule', metavar='security_group_rules',
            help=_('The limit of security groups rules'))
        return parser

    def _validate_int(self, name, value):
        try:
            return_value = int(value)
        except Exception:
            message = (_('Quota limit for %(name)s must be an integer') %
                       {'name': name})
            raise exceptions.NeutronClientException(message=message)
        return return_value

    def args2body(self, parsed_args):
        quota = {}
        for resource in ('network', 'subnet', 'port', 'router', 'floatingip',
                         'security_group', 'security_group_rule'):
            if getattr(parsed_args, resource):
                quota[resource] = self._validate_int(
                    resource,
                    getattr(parsed_args, resource))
        return {self.resource: quota}

    def get_data(self, parsed_args):
        self.log.debug('run(%s)', parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _extra_values = neutronV20.parse_args_to_dict(self.values_specs)
        neutronV20._merge_args(self, parsed_args, _extra_values,
                               self.values_specs)
        body = self.args2body(parsed_args)
        if self.resource in body:
            body[self.resource].update(_extra_values)
        else:
            body[self.resource] = _extra_values
        obj_updator = getattr(neutron_client,
                              "update_%s" % self.resource)
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  neutron_client)
        data = obj_updator(tenant_id, body)
        if self.resource in data:
            for k, v in data[self.resource].iteritems():
                if isinstance(v, list):
                    value = ""
                    for _item in v:
                        if value:
                            value += "\n"
                        if isinstance(_item, dict):
                            value += utils.dumps(_item)
                        else:
                            value += str(_item)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''
            return zip(*sorted(data[self.resource].iteritems()))
        else:
            return None
