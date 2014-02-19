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

import logging

from neutronclient.neutron import v2_0 as cmd_base
from neutronclient.openstack.common.gettextutils import _


class ListExt(cmd_base.ListCommand):
    """List all extensions."""

    resource = 'extension'
    log = logging.getLogger(__name__ + '.ListExt')
    list_columns = ['alias', 'name']


class ShowExt(cmd_base.ShowCommand):
    """Show information of a given resource."""

    resource = "extension"
    log = logging.getLogger(__name__ + '.ShowExt')
    allow_names = False

    def get_parser(self, prog_name):
        parser = super(cmd_base.ShowCommand, self).get_parser(prog_name)
        cmd_base.add_show_list_common_argument(parser)
        parser.add_argument(
            'id', metavar='EXT-ALIAS',
            help=_('The extension alias'))
        return parser
