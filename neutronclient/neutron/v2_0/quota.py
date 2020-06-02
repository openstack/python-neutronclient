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

import abc
import argparse

from cliff import lister
from cliff import show
from oslo_serialization import jsonutils

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


def get_tenant_id(args, client):
    return (args.pos_tenant_id or args.tenant_id or
            client.get_quotas_tenant()['tenant']['tenant_id'])


class DeleteQuota(neutronV20.NeutronCommand):
    """Delete defined quotas of a given tenant."""

    resource = 'quota'

    def get_parser(self, prog_name):
        parser = super(DeleteQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID.'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        parser.add_argument(
            'pos_tenant_id',
            help=argparse.SUPPRESS, nargs='?')
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        tenant_id = get_tenant_id(parsed_args, neutron_client)
        obj_deleter = getattr(neutron_client,
                              "delete_%s" % self.resource)
        obj_deleter(tenant_id)
        print((_('Deleted %(resource)s: %(tenant_id)s')
               % {'tenant_id': tenant_id,
                  'resource': self.resource}),
              file=self.app.stdout)
        return


class ListQuota(neutronV20.NeutronCommand, lister.Lister):
    """List quotas of all tenants who have non-default quota values."""

    resource = 'quota'

    def get_parser(self, prog_name):
        parser = super(ListQuota, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        search_opts = {}
        self.log.debug('search options: %s', search_opts)
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


class ShowQuotaBase(neutronV20.NeutronCommand, show.ShowOne):
    """Base class to show quotas of a given tenant."""

    resource = "quota"

    @abc.abstractmethod
    def retrieve_data(self, tenant_id, neutron_client):
        """Retrieve data using neutron client for the given tenant."""

    def get_parser(self, prog_name):
        parser = super(ShowQuotaBase, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID.'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        # allow people to do neutron quota-show <tenant-id>.
        # we use a different name for this because the default will
        # override whatever is in the named arg otherwise.
        parser.add_argument(
            'pos_tenant_id',
            help=argparse.SUPPRESS, nargs='?')
        return parser

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
        tenant_id = get_tenant_id(parsed_args, neutron_client)
        data = self.retrieve_data(tenant_id, neutron_client)
        if self.resource in data:
            return zip(*sorted(data[self.resource].items()))
        return


class ShowQuota(ShowQuotaBase):
    """Show quotas for a given tenant."""

    def retrieve_data(self, tenant_id, neutron_client):
        return neutron_client.show_quota(tenant_id)


class ShowQuotaDefault(ShowQuotaBase):
    """Show default quotas for a given tenant."""

    def retrieve_data(self, tenant_id, neutron_client):
        return neutron_client.show_quota_default(tenant_id)


class UpdateQuota(neutronV20.NeutronCommand, show.ShowOne):
    """Update a given tenant's quotas."""

    resource = 'quota'

    def get_parser(self, prog_name):
        parser = super(UpdateQuota, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID.'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--network', metavar='networks',
            help=_('The limit of networks.'))
        parser.add_argument(
            '--subnet', metavar='subnets',
            help=_('The limit of subnets.'))
        parser.add_argument(
            '--port', metavar='ports',
            help=_('The limit of ports.'))
        parser.add_argument(
            '--router', metavar='routers',
            help=_('The limit of routers.'))
        parser.add_argument(
            '--floatingip', metavar='floatingips',
            help=_('The limit of floating IPs.'))
        parser.add_argument(
            '--security-group', metavar='security_groups',
            help=_('The limit of security groups.'))
        parser.add_argument(
            '--security-group-rule', metavar='security_group_rules',
            help=_('The limit of security groups rules.'))
        parser.add_argument(
            '--vip', metavar='vips',
            help=_('The limit of vips.'))
        parser.add_argument(
            '--pool', metavar='pools',
            help=_('The limit of pools.'))
        parser.add_argument(
            '--member', metavar='members',
            help=_('The limit of pool members.'))
        parser.add_argument(
            '--health-monitor', metavar='health_monitors',
            dest='healthmonitor',
            help=_('The limit of health monitors.'))
        parser.add_argument(
            '--loadbalancer', metavar='loadbalancers',
            help=_('The limit of load balancers.'))
        parser.add_argument(
            '--listener', metavar='listeners',
            help=_('The limit of listeners.'))
        parser.add_argument(
            '--rbac-policy', metavar='rbac_policies',
            help=_('The limit of RBAC policies.'))
        parser.add_argument(
            'pos_tenant_id',
            help=argparse.SUPPRESS, nargs='?')

        return parser

    def _validate_int(self, name, value):
        try:
            return_value = int(value)
        except Exception:
            message = (_('Quota limit for %(name)s must be an integer') %
                       {'name': name})
            raise exceptions.CommandError(message=message)
        return return_value

    def args2body(self, parsed_args):
        quota = {}
        for resource in ('network', 'subnet', 'port', 'router', 'floatingip',
                         'security_group', 'security_group_rule',
                         'vip', 'pool', 'member', 'healthmonitor',
                         'loadbalancer', 'listener', 'rbac_policy'):
            if getattr(parsed_args, resource):
                quota[resource] = self._validate_int(
                    resource,
                    getattr(parsed_args, resource))
        if not quota:
            raise exceptions.CommandError(
                message=_('Must specify a valid resource with new quota '
                          'value'))
        return {self.resource: quota}

    def take_action(self, parsed_args):
        neutron_client = self.get_client()
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
        tenant_id = get_tenant_id(parsed_args, neutron_client)
        data = obj_updator(tenant_id, body)
        if self.resource in data:
            for k, v in data[self.resource].items():
                if isinstance(v, list):
                    value = ""
                    for _item in v:
                        if value:
                            value += "\n"
                        if isinstance(_item, dict):
                            value += jsonutils.dumps(_item)
                        else:
                            value += str(_item)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''
            return zip(*sorted(data[self.resource].items()))
        else:
            return
