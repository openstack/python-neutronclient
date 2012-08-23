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

import logging

from cliff import lister
from cliff import show

from quantumclient.common import utils
from quantumclient.quantum.v2_0 import QuantumCommand


class ListExt(QuantumCommand, lister.Lister):
    """List all exts."""

    api = 'network'
    resource = 'extension'
    log = logging.getLogger(__name__ + '.ListExt')
    _formatters = None

    def get_parser(self, prog_name):
        parser = super(ListExt, self).get_parser(prog_name)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        search_opts = {}
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


class ShowExt(QuantumCommand, show.ShowOne):
    """Show information of a given resource

    """
    api = 'network'
    resource = "extension"
    log = logging.getLogger(__name__ + '.ShowExt')

    def get_parser(self, prog_name):
        parser = super(ShowExt, self).get_parser(prog_name)
        parser.add_argument(
            'ext_alias', metavar='ext-alias',
            help='the extension alias')
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        params = {}
        obj_shower = getattr(quantum_client,
                             "show_%s" % self.resource)
        data = obj_shower(parsed_args.ext_alias, **params)
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
