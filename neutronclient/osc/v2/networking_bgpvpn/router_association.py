# Copyright (c) 2016 Juniper networks Inc.
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

from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.osc.v2.networking_bgpvpn import constants
from neutronclient.osc.v2.networking_bgpvpn.resource_association import\
    CreateBgpvpnResAssoc
from neutronclient.osc.v2.networking_bgpvpn.resource_association import\
    DeleteBgpvpnResAssoc
from neutronclient.osc.v2.networking_bgpvpn.resource_association import\
    ListBgpvpnResAssoc
from neutronclient.osc.v2.networking_bgpvpn.resource_association import\
    SetBgpvpnResAssoc
from neutronclient.osc.v2.networking_bgpvpn.resource_association import\
    ShowBgpvpnResAssoc
from neutronclient.osc.v2.networking_bgpvpn.resource_association import\
    UnsetBgpvpnResAssoc


class BgpvpnRouterAssoc(object):
    _assoc_res_name = constants.ROUTER_RESOURCE_NAME
    _resource = constants.ROUTER_ASSOC
    _resource_plural = constants.ROUTER_ASSOCS

    _attr_map = (
        ('id', 'ID', column_util.LIST_BOTH),
        ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
        ('%s_id' % _assoc_res_name, '%s ID' % _assoc_res_name.capitalize(),
         column_util.LIST_BOTH),
        ('advertise_extra_routes', 'Advertise extra routes',
         column_util.LIST_LONG_ONLY),
    )
    _formatters = {}

    def _get_common_parser(self, parser):
        """Adds to parser arguments common to create, set and unset commands.

        :params ArgumentParser parser: argparse object contains all command's
                                       arguments
        """
        ADVERTISE_ROUTES = _("Routes will be advertised to the "
                             "BGP VPN%s") % (
                                 _(' (default)') if self._action == 'create'
                                 else "")
        NOT_ADVERTISE_ROUTES = _("Routes from the router will not be "
                                 "advertised to the BGP VPN")

        group_advertise_extra_routes = parser.add_mutually_exclusive_group()
        group_advertise_extra_routes.add_argument(
            '--advertise_extra_routes',
            action='store_true',
            help=NOT_ADVERTISE_ROUTES if self._action == 'unset'
            else ADVERTISE_ROUTES,
        )
        group_advertise_extra_routes.add_argument(
            '--no-advertise_extra_routes',
            action='store_true',
            help=ADVERTISE_ROUTES if self._action == 'unset'
            else NOT_ADVERTISE_ROUTES,
        )

    def _args2body(self, _, args):
        attrs = {}

        if args.advertise_extra_routes:
            attrs['advertise_extra_routes'] = self._action != 'unset'
        elif args.no_advertise_extra_routes:
            attrs['advertise_extra_routes'] = self._action == 'unset'

        return {self._resource: attrs}


class CreateBgpvpnRouterAssoc(BgpvpnRouterAssoc, CreateBgpvpnResAssoc):
    _description = _("Create a BGP VPN router association")
    pass


class SetBgpvpnRouterAssoc(BgpvpnRouterAssoc, SetBgpvpnResAssoc):
    _description = _("Set BGP VPN router association properties")


class UnsetBgpvpnRouterAssoc(BgpvpnRouterAssoc, UnsetBgpvpnResAssoc):
    _description = _("Unset BGP VPN router association properties")


class DeleteBgpvpnRouterAssoc(BgpvpnRouterAssoc, DeleteBgpvpnResAssoc):
    _description = _("Delete a BGP VPN router association(s) for a given BGP "
                     "VPN")
    pass


class ListBgpvpnRouterAssoc(BgpvpnRouterAssoc, ListBgpvpnResAssoc):
    _description = _("List BGP VPN router associations for a given BGP VPN")
    pass


class ShowBgpvpnRouterAssoc(BgpvpnRouterAssoc, ShowBgpvpnResAssoc):
    _description = _("Show information of a given BGP VPN router association")
    pass
