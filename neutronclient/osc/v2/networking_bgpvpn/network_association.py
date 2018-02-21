# Copyright (c) 2016 Juniper Networks Inc.
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


class BgpvpnNetAssoc(object):
    _assoc_res_name = constants.NETWORK_RESOURCE_NAME
    _resource = constants.NETWORK_ASSOC
    _resource_plural = constants.NETWORK_ASSOCS

    _attr_map = (
        ('id', 'ID', column_util.LIST_BOTH),
        ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
        ('%s_id' % _assoc_res_name, '%s ID' % _assoc_res_name.capitalize(),
         column_util.LIST_BOTH),
    )
    _formatters = {}


class CreateBgpvpnNetAssoc(BgpvpnNetAssoc, CreateBgpvpnResAssoc):
    _description = _("Create a BGP VPN network association")
    pass


class DeleteBgpvpnNetAssoc(BgpvpnNetAssoc, DeleteBgpvpnResAssoc):
    _description = _("Delete a BGP VPN network association(s) for a given BGP "
                     "VPN")
    pass


class ListBgpvpnNetAssoc(BgpvpnNetAssoc, ListBgpvpnResAssoc):
    _description = _("List BGP VPN network associations for a given BGP VPN")
    pass


class ShowBgpvpnNetAssoc(BgpvpnNetAssoc, ShowBgpvpnResAssoc):
    _description = _("Show information of a given BGP VPN network association")
    pass
