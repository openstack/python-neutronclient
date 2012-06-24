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

from quantumclient.common import command
from quantumclient.common import exceptions
from quantumclient.common import utils


def add_show_list_common_argument(parser):
    parser.add_argument(
        '-D', '--show-details',
        help='show detailed info',
        action='store_true',
        default=False, )
    parser.add_argument(
        '-F', '--fields',
        help='specify the field(s) to be returned by server,'
        ' can be repeated',
        action='append',
        default=[], )


def add_extra_argument(parser, name, _help):
    parser.add_argument(
        name,
        nargs=argparse.REMAINDER,
        help=_help + ': --key1 [type=int|bool|...] value '
                     '[--key2 [type=int|bool|...] value ...]')


def parse_args_to_dict(values_specs):
    '''It is used to analyze the extra command options to command.

    Besides known options and arguments, our commands also support user to
    put more options to the end of command line. For example,
    list_nets -- --tag x y --key1 value1, where '-- --tag x y --key1 value1'
    is extra options to our list_nets. This feature can support V2.0 API's
    fields selection and filters. For example, to list networks which has name
    'test4', we can have list_nets -- --name=test4.

    value spec is: --key type=int|bool|... value. Type is one of Python
    built-in types. By default, type is string. The key without value is
    a bool option. Key with two values will be a list option.

    '''
    # -- is a pseudo argument
    if values_specs and values_specs[0] == '--':
        del values_specs[0]
    _options = {}
    current_arg = None
    _values_specs = []
    _value_number = 0
    _list_flag = False
    current_item = None
    for _item in values_specs:
        if _item.startswith('--'):
            if current_arg is not None:
                if _value_number > 1 or _list_flag:
                    current_arg.update({'nargs': '+'})
                elif _value_number == 0:
                    current_arg.update({'action': 'store_true'})
            _temp = _item
            if "=" in _item:
                _item = _item.split('=')[0]
            if _item in _options:
                raise exceptions.CommandError(
                    "duplicated options %s" % ' '.join(values_specs))
            else:
                _options.update({_item: {}})
            current_arg = _options[_item]
            _item = _temp
        elif _item.startswith('type='):
            if current_arg is not None:
                _type_str = _item.split('=', 2)[1]
                current_arg.update({'type': eval(_type_str)})
                if _type_str == 'bool':
                    current_arg.update({'type': utils.str2bool})
                elif _type_str == 'dict':
                    current_arg.update({'type': utils.str2dict})
                continue
            else:
                raise exceptions.CommandError(
                    "invalid values_specs %s" % ' '.join(values_specs))
        elif _item == 'list=true':
            _list_flag = True
            continue
        if not _item.startswith('--'):
            if not current_item or '=' in current_item:
                raise exceptions.CommandError(
                    "Invalid values_specs %s" % ' '.join(values_specs))
            _value_number += 1
        elif _item.startswith('--'):
            current_item = _item
            if '=' in current_item:
                _value_number = 1
            else:
                _value_number = 0
            _list_flag = False
        _values_specs.append(_item)
    if current_arg is not None:
        if _value_number > 1 or _list_flag:
            current_arg.update({'nargs': '+'})
        elif _value_number == 0:
            current_arg.update({'action': 'store_true'})
    _parser = argparse.ArgumentParser(add_help=False)
    for opt, optspec in _options.iteritems():
        _parser.add_argument(opt, **optspec)
    _args = _parser.parse_args(_values_specs)
    result_dict = {}
    for opt in _options.iterkeys():
        _opt = opt.split('--', 2)[1]
        _value = getattr(_args, _opt.replace('-', '_'))
        if _value is not None:
            result_dict.update({_opt: _value})
    return result_dict


class QuantumCommand(command.OpenStackCommand):
    api = 'network'
    log = logging.getLogger(__name__ + '.QuantumCommand')

    def get_client(self):
        return self.app.client_manager.quantum

    def get_parser(self, prog_name):
        parser = super(QuantumCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--request-format',
            help=_('the xml or json request format'),
            default='json',
            choices=['json', 'xml', ], )

        return parser


class CreateCommand(QuantumCommand, show.ShowOne):
    """Create a resource for a given tenant

    """

    api = 'network'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(CreateCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('the owner tenant ID'), )
        self.add_known_arguments(parser)
        add_extra_argument(parser, 'value_specs',
                           'new values for the %s' % self.resource)
        return parser

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        return {}

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _extra_values = parse_args_to_dict(parsed_args.value_specs)
        body[self.resource].update(_extra_values)
        obj_creator = getattr(quantum_client,
                              "create_%s" % self.resource)
        data = obj_creator(body)
        # {u'network': {u'id': u'e9424a76-6db4-4c93-97b6-ec311cd51f19'}}
        info = self.resource in data and data[self.resource] or None
        if info:
            print >>self.app.stdout, _('Created a new %s:' % self.resource)
        else:
            info = {'': ''}
        for k, v in info.iteritems():
            if isinstance(v, list):
                value = ""
                for _item in v:
                    if value:
                        value += "\n"
                    if isinstance(_item, dict):
                        value += utils.dumps(_item)
                    else:
                        value += str(_item)
                info[k] = value
            elif v is None:
                info[k] = ''
        return zip(*sorted(info.iteritems()))


class UpdateCommand(QuantumCommand):
    """Update resource's information
    """

    api = 'network'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(UpdateCommand, self).get_parser(prog_name)
        parser.add_argument(
            'id', metavar='%s-id' % self.resource,
            help='ID of %s to update' % self.resource)
        add_extra_argument(parser, 'value_specs',
                           'new values for the %s' % self.resource)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        value_specs = parsed_args.value_specs
        if not value_specs:
            raise exceptions.CommandError(
                "Must specify new values to update %s" % self.resource)
        data = {self.resource: parse_args_to_dict(value_specs)}
        obj_updator = getattr(quantum_client,
                              "update_%s" % self.resource)
        obj_updator(parsed_args.id, data)
        print >>self.app.stdout, (
            _('Updated %(resource)s: %(id)s') %
            {'id': parsed_args.id, 'resource': self.resource})
        return


class DeleteCommand(QuantumCommand):
    """Delete a given resource

    """

    api = 'network'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(DeleteCommand, self).get_parser(prog_name)
        parser.add_argument(
            'id', metavar='%s-id' % self.resource,
            help='ID of %s to delete' % self.resource)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        obj_deleter = getattr(quantum_client,
                              "delete_%s" % self.resource)
        obj_deleter(parsed_args.id)
        print >>self.app.stdout, (_('Deleted %(resource)s: %(id)s')
                                  % {'id': parsed_args.id,
                                     'resource': self.resource})
        return


class ListCommand(QuantumCommand, lister.Lister):
    """List resourcs that belong to a given tenant

    """

    api = 'network'
    resource = None
    log = None
    _formatters = None

    def get_parser(self, prog_name):
        parser = super(ListCommand, self).get_parser(prog_name)
        add_show_list_common_argument(parser)
        add_extra_argument(parser, 'filter_specs', 'filters options')
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        search_opts = parse_args_to_dict(parsed_args.filter_specs)

        self.log.debug('search options: %s', search_opts)
        quantum_client.format = parsed_args.request_format
        fields = parsed_args.fields
        extra_fields = search_opts.get('fields', [])
        if extra_fields:
            if isinstance(extra_fields, list):
                fields.extend(extra_fields)
            else:
                fields.append(extra_fields)
        if fields:
            search_opts.update({'fields': fields})
        if parsed_args.show_details:
            search_opts.update({'verbose': 'True'})
        obj_lister = getattr(quantum_client,
                             "list_%ss" % self.resource)

        data = obj_lister(**search_opts)
        info = []
        collection = self.resource + "s"
        if collection in data:
            info = data[collection]
        _columns = len(info) > 0 and sorted(info[0].keys()) or []
        return (_columns, (utils.get_item_properties(
            s, _columns, formatters=self._formatters, )
            for s in info), )


class ShowCommand(QuantumCommand, show.ShowOne):
    """Show information of a given resource

    """

    api = 'network'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        add_show_list_common_argument(parser)
        parser.add_argument(
            'id', metavar='%s-id' % self.resource,
            help='ID of %s to look up' % self.resource)

        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        params = {}
        if parsed_args.show_details:
            params = {'verbose': 'True'}
        if parsed_args.fields:
            params = {'fields': parsed_args.fields}
        obj_showor = getattr(quantum_client,
                             "show_%s" % self.resource)
        data = obj_showor(parsed_args.id, **params)
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
