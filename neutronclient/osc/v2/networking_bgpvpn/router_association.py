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
    ShowBgpvpnResAssoc


class BgpvpnRouterAssoc(object):
    _assoc_res_name = constants.ROUTER_RESOURCE_NAME
    _resource = constants.ROUTER_ASSOC
    _resource_plural = constants.ROUTER_ASSOCS

    _attr_map = (
        ('id', 'ID', column_util.LIST_BOTH),
        ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
        ('%s_id' % _assoc_res_name, '%s ID' % _assoc_res_name.capitalize(),
         column_util.LIST_BOTH),
    )
    _formatters = {}


class CreateBgpvpnRouterAssoc(BgpvpnRouterAssoc, CreateBgpvpnResAssoc):
    _description = _("Create a BGP VPN router association")
    pass


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
