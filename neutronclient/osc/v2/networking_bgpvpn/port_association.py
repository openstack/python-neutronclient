# Copyright (c) 2017 Juniper networks Inc.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import logging

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.osc.v2.networking_bgpvpn import constants
from neutronclient.osc.v2.networking_bgpvpn import resource_association

LOG = logging.getLogger(__name__)


class BgpvpnPortAssoc(object):
    _assoc_res_name = constants.PORT_RESOURCE_NAME
    _resource = constants.PORT_ASSOC
    _resource_plural = constants.PORT_ASSOCS

    _attr_map = (
        ('id', 'ID', column_util.LIST_BOTH),
        ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
        ('%s_id' % _assoc_res_name, '%s ID' % _assoc_res_name.capitalize(),
         column_util.LIST_BOTH),
        ('prefix_routes', 'Prefix Routes (BGP LOCAL_PREF)',
         column_util.LIST_LONG_ONLY),
        ('bgpvpn_routes', 'BGP VPN Routes (BGP LOCAL_PREF)',
         column_util.LIST_LONG_ONLY),
        ('advertise_fixed_ips', "Advertise Port's Fixed IPs",
         column_util.LIST_LONG_ONLY),
    )
    _formatters = {
        'prefix_routes': format_columns.ListColumn,
        'bgpvpn_routes': format_columns.ListColumn,
    }

    def _transform_resource(self, data):
        """Transforms BGP VPN port association routes property

        That permits to easily format the command output with ListColumn
        formater and separate the two route types.

        {'routes':
            [
                {
                    'type': 'prefix',
                    'local_pref': 100,
                    'prefix': '8.8.8.0/27',
                },
                {
                    'type': 'prefix',
                    'local_pref': 42,
                    'prefix': '80.50.30.0/28',
                },
                {
                    'type': 'bgpvpn',
                    'local_pref': 50,
                    'bgpvpn': '157d72a9-9968-48e7-8087-6c9a9bc7a181',
                },
                {
                    'type': 'bgpvpn',
                    'bgpvpn': 'd5c7aaab-c7e8-48b3-85ca-a115c00d3603',
                },
            ],
        }

        to

        {
            'prefix_routes': [
                '8.8.8.0/27 (100)',
                '80.50.30.0/28 (42)',
            ],
            'bgpvpn_routes': [
                '157d72a9-9968-48e7-8087-6c9a9bc7a181 (50)',
                'd5c7aaab-c7e8-48b3-85ca-a115c00d3603',
            ],
        }
        """
        for route in data.get('routes', []):
            local_pref = ''
            if route.get('local_pref'):
                local_pref = ' (%d)' % route.get('local_pref')
            if route['type'] == 'prefix':
                data.setdefault('prefix_routes', []).append(
                    '%s%s' % (route['prefix'], local_pref)
                )
            elif route['type'] == 'bgpvpn':
                data.setdefault('bgpvpn_routes', []).append(
                    '%s%s' % (route['bgpvpn_id'], local_pref)
                )
            else:
                LOG.warning("Unknown route type %s (%s).", route['type'],
                            route)
        data.pop('routes', None)

    def _get_common_parser(self, parser):
        """Adds to parser arguments common to create, set and unset commands.

        :params ArgumentParser parser: argparse object contains all command's
                                       arguments
        """
        ADVERTISE_ROUTE = _("Fixed IPs of the port will be advertised to the "
                            "BGP VPN%s") % (
                                _(' (default)') if self._action == 'create'
                                else "")
        NOT_ADVERTISE_ROUTE = _("Fixed IPs of the port will not be advertised "
                                "to the BGP VPN")

        LOCAL_PREF_VALUE = _(". Optionally, can control the value of the BGP "
                             "LOCAL_PREF of the routes that will be "
                             "advertised")

        ADD_PREFIX_ROUTE = _("Add prefix route in CIDR notation%s") %\
            LOCAL_PREF_VALUE
        REMOVE_PREFIX_ROUTE = _("Remove prefix route in CIDR notation")
        REPEAT_PREFIX_ROUTE = _("repeat option for multiple prefix routes")

        ADD_BGVPVPN_ROUTE = _("Add BGP VPN route for route leaking%s") %\
            LOCAL_PREF_VALUE
        REMOVE_BGPVPN_ROUTE = _("Remove BGP VPN route")
        REPEAT_BGPVPN_ROUTE = _("repeat option for multiple BGP VPN routes")

        group_advertise_fixed_ips = parser.add_mutually_exclusive_group()
        group_advertise_fixed_ips.add_argument(
            '--advertise-fixed-ips',
            action='store_true',
            help=NOT_ADVERTISE_ROUTE if self._action == 'unset'
            else ADVERTISE_ROUTE,
        )
        group_advertise_fixed_ips.add_argument(
            '--no-advertise-fixed-ips',
            action='store_true',
            help=ADVERTISE_ROUTE if self._action == 'unset'
            else NOT_ADVERTISE_ROUTE,
        )

        if self._action in ['create', 'set']:
            parser.add_argument(
                '--prefix-route',
                metavar="prefix=<cidr>[,local_pref=<integer>]",
                dest='prefix_routes',
                action=parseractions.MultiKeyValueAction,
                required_keys=['prefix'],
                optional_keys=['local_pref'],
                help="%s (%s)" % (ADD_PREFIX_ROUTE, REPEAT_PREFIX_ROUTE),
            )
            parser.add_argument(
                '--bgpvpn-route',
                metavar="bgpvpn=<BGP VPN ID or name>[,local_pref=<integer>]",
                dest='bgpvpn_routes',
                action=parseractions.MultiKeyValueAction,
                required_keys=['bgpvpn'],
                optional_keys=['local_pref'],
                help="%s (%s)" % (ADD_BGVPVPN_ROUTE, REPEAT_BGPVPN_ROUTE),
            )
        else:
            parser.add_argument(
                '--prefix-route',
                metavar="<cidr>",
                dest='prefix_routes',
                action='append',
                help="%s (%s)" % (REMOVE_PREFIX_ROUTE, REPEAT_PREFIX_ROUTE),
            )
            parser.add_argument(
                '--bgpvpn-route',
                metavar="<BGP VPN ID or name>",
                dest='bgpvpn_routes',
                action='append',
                help="%s (%s)" % (REMOVE_BGPVPN_ROUTE, REPEAT_BGPVPN_ROUTE),
            )
        if self._action != 'create':
            parser.add_argument(
                '--no-prefix-route' if self._action == 'set' else
                '--all-prefix-routes',
                dest='purge_prefix_route',
                action='store_true',
                help=_('Empty prefix route list'),
            )
            parser.add_argument(
                '--no-bgpvpn-route' if self._action == 'set' else
                '--all-bgpvpn-routes',
                dest='purge_bgpvpn_route',
                action='store_true',
                help=_('Empty BGP VPN route list'),
            )

    def _args2body(self, bgpvpn_id, args):
        client = self.app.client_manager.neutronclient
        attrs = {}

        if self._action != 'create':
            assoc = client.find_resource_by_id(
                self._resource,
                args.resource_association_id,
                cmd_resource='bgpvpn_%s_assoc' % self._assoc_res_name,
                parent_id=bgpvpn_id)
        else:
            assoc = {'routes': []}

        if args.advertise_fixed_ips:
            attrs['advertise_fixed_ips'] = self._action != 'unset'
        elif args.no_advertise_fixed_ips:
            attrs['advertise_fixed_ips'] = self._action == 'unset'

        prefix_routes = None
        if 'purge_prefix_route' in args and args.purge_prefix_route:
            prefix_routes = []
        else:
            prefix_routes = {r['prefix']: r.get('local_pref')
                             for r in assoc['routes']
                             if r['type'] == 'prefix'}
            if args.prefix_routes:
                if self._action in ['create', 'set']:
                    prefix_routes.update({r['prefix']: r.get('local_pref')
                                          for r in args.prefix_routes})
                elif self._action == 'unset':
                    for prefix in args.prefix_routes:
                        prefix_routes.pop(prefix, None)

        bgpvpn_routes = None
        if 'purge_bgpvpn_route' in args and args.purge_bgpvpn_route:
            bgpvpn_routes = []
        else:
            bgpvpn_routes = {r['bgpvpn_id']: r.get('local_pref')
                             for r in assoc['routes']
                             if r['type'] == 'bgpvpn'}
            if args.bgpvpn_routes:
                if self._action == 'unset':
                    routes = [
                        {'bgpvpn': bgpvpn} for bgpvpn in args.bgpvpn_routes
                    ]
                else:
                    routes = args.bgpvpn_routes
                args_bgpvpn_routes = {
                    client.find_resource(constants.BGPVPN, r['bgpvpn'])['id']:
                        r.get('local_pref')
                    for r in routes
                }
                if self._action in ['create', 'set']:
                    bgpvpn_routes.update(args_bgpvpn_routes)
                elif self._action == 'unset':
                    for bgpvpn_id in args_bgpvpn_routes:
                        bgpvpn_routes.pop(bgpvpn_id, None)

        if prefix_routes is not None and not prefix_routes:
            attrs.setdefault('routes', [])
        elif prefix_routes is not None:
            for prefix, local_pref in prefix_routes.items():
                route = {
                    'type': 'prefix',
                    'prefix': prefix,
                }
                if local_pref:
                    route['local_pref'] = int(local_pref)
                attrs.setdefault('routes', []).append(route)
        if bgpvpn_routes is not None and not bgpvpn_routes:
            attrs.setdefault('routes', [])
        elif bgpvpn_routes is not None:
            for bgpvpn_id, local_pref in bgpvpn_routes.items():
                route = {
                    'type': 'bgpvpn',
                    'bgpvpn_id': bgpvpn_id,
                }
                if local_pref:
                    route['local_pref'] = int(local_pref)
                attrs.setdefault('routes', []).append(route)

        return {self._resource: attrs}


class CreateBgpvpnPortAssoc(BgpvpnPortAssoc,
                            resource_association.CreateBgpvpnResAssoc):
    _description = _("Create a BGP VPN port association")


class SetBgpvpnPortAssoc(BgpvpnPortAssoc,
                         resource_association.SetBgpvpnResAssoc):
    _description = _("Set BGP VPN port association properties")


class UnsetBgpvpnPortAssoc(BgpvpnPortAssoc,
                           resource_association.UnsetBgpvpnResAssoc):
    _description = _("Unset BGP VPN port association properties")


class DeleteBgpvpnPortAssoc(BgpvpnPortAssoc,
                            resource_association.DeleteBgpvpnResAssoc):
    _description = _("Delete a BGP VPN port association(s) for a given BGP "
                     "VPN")


class ListBgpvpnPortAssoc(BgpvpnPortAssoc,
                          resource_association.ListBgpvpnResAssoc):
    _description = _("List BGP VPN port associations for a given BGP VPN")


class ShowBgpvpnPortAssoc(BgpvpnPortAssoc,
                          resource_association.ShowBgpvpnResAssoc):
    _description = _("Show information of a given BGP VPN port association")
