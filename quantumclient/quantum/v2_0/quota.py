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

import argparse
import logging

from cliff import lister
from cliff import show

from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient.quantum import v2_0 as quantumv20
from quantumclient.quantum.v2_0 import QuantumCommand


def get_tenant_id(tenant_id, client):
    return (tenant_id if tenant_id else
            client.get_quotas_tenant()['tenant']['tenant_id'])


class DeleteQuota(QuantumCommand):
    """Delete defined quotas of a given tenant."""

    api = 'network'
    resource = 'quota'
    log = logging.getLogger(__name__ + '.DeleteQuota')

    def get_parser(self, prog_name):
        parser = super(DeleteQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help='the owner tenant ID')
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  quantum_client)
        obj_deleter = getattr(quantum_client,
                              "delete_%s" % self.resource)
        obj_deleter(tenant_id)
        print >>self.app.stdout, (_('Deleted %(resource)s: %(tenant_id)s')
                                  % {'tenant_id': tenant_id,
                                     'resource': self.resource})
        return


class ListQuota(QuantumCommand, lister.Lister):
    """List defined quotas of all tenants."""

    api = 'network'
    resource = 'quota'
    log = logging.getLogger(__name__ + '.ListQuota')
    _formatters = None

    def get_parser(self, prog_name):
        parser = super(ListQuota, self).get_parser(prog_name)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        search_opts = {}
        self.log.debug('search options: %s', search_opts)
        quantum_client.format = parsed_args.request_format
        obj_lister = getattr(quantum_client,
                             "list_%ss" % self.resource)
        data = obj_lister(**search_opts)
        info = []
        collection = self.resource + "s"
        if collection in data:
            info = data[collection]
        _columns = len(info) > 0 and sorted(info[0].keys()) or []
        return (_columns, (utils.get_item_properties(s, _columns)
                for s in info))


class ShowQuota(QuantumCommand, show.ShowOne):
    """Show quotas of a given tenant

    """
    api = 'network'
    resource = "quota"
    log = logging.getLogger(__name__ + '.ShowQuota')

    def get_parser(self, prog_name):
        parser = super(ShowQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help='the owner tenant ID')
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  quantum_client)
        params = {}
        obj_shower = getattr(quantum_client,
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


class UpdateQuota(QuantumCommand, show.ShowOne):
    """Define tenant's quotas not to use defaults."""

    resource = 'quota'
    log = logging.getLogger(__name__ + '.UpdateQuota')

    def get_parser(self, prog_name):
        parser = super(UpdateQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help='the owner tenant ID')
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--network', metavar='networks',
            help='the limit of network quota')
        parser.add_argument(
            '--subnet', metavar='subnets',
            help='the limit of subnet quota')
        parser.add_argument(
            '--port', metavar='ports',
            help='the limit of port quota')
        quantumv20.add_extra_argument(
            parser, 'value_specs',
            'new values for the %s' % self.resource)
        return parser

    def _validate_int(self, name, value):
        try:
            return_value = int(value)
        except Exception:
            message = (_('quota limit for %(name)s must be an integer') %
                       {'name': name})
            raise exceptions.QuantumClientException(message=message)
        return return_value

    def get_data(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        quota = {}
        for resource in ('network', 'subnet', 'port'):
            if getattr(parsed_args, resource):
                quota[resource] = self._validate_int(
                    resource,
                    getattr(parsed_args, resource))
        value_specs = parsed_args.value_specs
        if value_specs:
            quota.update(quantumv20.parse_args_to_dict(value_specs))
        obj_updator = getattr(quantum_client,
                              "update_%s" % self.resource)
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  quantum_client)
        data = obj_updator(tenant_id, {self.resource: quota})
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
