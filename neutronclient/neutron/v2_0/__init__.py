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
import functools
import logging

from cliff import command
from cliff import lister
from cliff import show
from oslo_serialization import jsonutils

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils

HYPHEN_OPTS = ['tags_any', 'not_tags', 'not_tags_any']


def find_resource_by_id(client, resource, resource_id, cmd_resource=None,
                        parent_id=None, fields=None):
    return client.find_resource_by_id(resource, resource_id, cmd_resource,
                                      parent_id, fields)


def find_resourceid_by_id(client, resource, resource_id, cmd_resource=None,
                          parent_id=None):
    return find_resource_by_id(client, resource, resource_id, cmd_resource,
                               parent_id, fields='id')['id']


def find_resource_by_name_or_id(client, resource, name_or_id,
                                project_id=None, cmd_resource=None,
                                parent_id=None, fields=None):
    return client.find_resource(resource, name_or_id, project_id,
                                cmd_resource, parent_id, fields)


def find_resourceid_by_name_or_id(client, resource, name_or_id,
                                  project_id=None, cmd_resource=None,
                                  parent_id=None):
    return find_resource_by_name_or_id(client, resource, name_or_id,
                                       project_id, cmd_resource,
                                       parent_id, fields='id')['id']


def add_show_list_common_argument(parser):
    parser.add_argument(
        '-D', '--show-details',
        help=_('Show detailed information.'),
        action='store_true',
        default=False, )
    parser.add_argument(
        '--show_details',
        action='store_true',
        help=argparse.SUPPRESS)
    parser.add_argument(
        '--fields',
        help=argparse.SUPPRESS,
        action='append',
        default=[])
    parser.add_argument(
        '-F', '--field',
        dest='fields', metavar='FIELD',
        help=_('Specify the field(s) to be returned by server. You can '
               'repeat this option.'),
        action='append',
        default=[])


def add_pagination_argument(parser):
    parser.add_argument(
        '-P', '--page-size',
        dest='page_size', metavar='SIZE', type=int,
        help=_("Specify retrieve unit of each request, then split one request "
               "to several requests."),
        default=None)


def add_sorting_argument(parser):
    parser.add_argument(
        '--sort-key',
        dest='sort_key', metavar='FIELD',
        action='append',
        help=_("Sorts the list by the specified fields in the specified "
               "directions. You can repeat this option, but you must "
               "specify an equal number of sort_dir and sort_key values. "
               "Extra sort_dir options are ignored. Missing sort_dir options "
               "use the default asc value."),
        default=[])
    parser.add_argument(
        '--sort-dir',
        dest='sort_dir', metavar='{asc,desc}',
        help=_("Sorts the list in the specified direction. You can repeat "
               "this option."),
        action='append',
        default=[],
        choices=['asc', 'desc'])


def is_number(s):
    try:
        float(s)  # for int, long and float
    except ValueError:
        try:
            complex(s)  # for complex
        except ValueError:
            return False

    return True


def _process_previous_argument(current_arg, _value_number, current_type_str,
                               _list_flag, _values_specs, _clear_flag,
                               values_specs):
    if current_arg is not None:
        if _value_number == 0 and (current_type_str or _list_flag):
            # This kind of argument should have value
            raise exceptions.CommandError(
                _("Invalid values_specs %s") % ' '.join(values_specs))
        if _value_number > 1 or _list_flag or current_type_str == 'list':
            current_arg.update({'nargs': '+'})
        elif _value_number == 0:
            if _clear_flag:
                # if we have action=clear, we use argument's default
                # value None for argument
                _values_specs.pop()
            else:
                # We assume non value argument as bool one
                current_arg.update({'action': 'store_true'})


def parse_args_to_dict(values_specs):
    """It is used to analyze the extra command options to command.

    Besides known options and arguments, our commands also support user to
    put more options to the end of command line. For example,
    list_nets -- --tag x y --key1 value1, where '-- --tag x y --key1 value1'
    is extra options to our list_nets. This feature can support V2.0 API's
    fields selection and filters. For example, to list networks which has name
    'test4', we can have list_nets -- --name=test4.

    value spec is: --key type=int|bool|... value. Type is one of Python
    built-in types. By default, type is string. The key without value is
    a bool option. Key with two values will be a list option.
    """

    # values_specs for example: '-- --tag x y --key1 type=int value1'
    # -- is a pseudo argument
    values_specs_copy = values_specs[:]
    if values_specs_copy and values_specs_copy[0] == '--':
        del values_specs_copy[0]
    # converted ArgumentParser arguments for each of the options
    _options = {}
    # the argument part for current option in _options
    current_arg = None
    # the string after remove meta info in values_specs
    # for example, '--tag x y --key1 value1'
    _values_specs = []
    # record the count of values for an option
    # for example: for '--tag x y', it is 2, while for '--key1 value1', it is 1
    _value_number = 0
    # list=true
    _list_flag = False
    # action=clear
    _clear_flag = False
    # the current item in values_specs
    current_item = None
    # the str after 'type='
    current_type_str = None
    # dict of allowed types
    allowed_type_dict = {
        'bool': utils.str2bool,
        'dict': utils.str2dict,
        'int': int,
        'str': str,
    }

    for _item in values_specs_copy:
        if _item.startswith('--'):
            # Deal with previous argument if any
            _process_previous_argument(
                current_arg, _value_number, current_type_str,
                _list_flag, _values_specs, _clear_flag, values_specs)

            # Init variables for current argument
            current_item = _item
            _list_flag = False
            _clear_flag = False
            current_type_str = None
            if "=" in _item:
                _value_number = 1
                _item = _item.split('=')[0]
            else:
                _value_number = 0
            if _item in _options:
                raise exceptions.CommandError(
                    _("Duplicated options %s") % ' '.join(values_specs))
            else:
                _options.update({_item: {}})
            current_arg = _options[_item]
            _item = current_item
        elif _item.startswith('type='):
            if current_arg is None:
                raise exceptions.CommandError(
                    _("Invalid values_specs %s") % ' '.join(values_specs))
            if 'type' not in current_arg:
                current_type_str = _item.split('=', 2)[1]
                if current_type_str in allowed_type_dict:
                    current_arg['type'] = allowed_type_dict[current_type_str]
                    continue
                else:
                    raise exceptions.CommandError(
                        _("Invalid value_specs {valspec}: type {curtypestr}"
                            " is not supported").format(
                            valspec=' '.join(values_specs),
                            curtypestr=current_type_str))

        elif _item == 'list=true':
            _list_flag = True
            continue
        elif _item == 'action=clear':
            _clear_flag = True
            continue

        if not _item.startswith('--'):
            # All others are value items
            # Make sure '--' occurs first and allow minus value
            if (not current_item or '=' in current_item or
                    _item.startswith('-') and not is_number(_item)):
                raise exceptions.CommandError(
                    _("Invalid values_specs %s") % ' '.join(values_specs))
            _value_number += 1

        if _item.startswith('---'):
            raise exceptions.CommandError(
                _("Invalid values_specs %s") % ' '.join(values_specs))
        _values_specs.append(_item)

    # Deal with last one argument
    _process_previous_argument(
        current_arg, _value_number, current_type_str,
        _list_flag, _values_specs, _clear_flag, values_specs)

    # Populate the parser with arguments
    _parser = argparse.ArgumentParser(add_help=False)
    for opt, optspec in _options.items():
        _parser.add_argument(opt, **optspec)
    _args = _parser.parse_args(_values_specs)

    result_dict = {}
    for opt in _options.keys():
        _opt = opt.split('--', 2)[1]
        _opt = _opt.replace('-', '_')
        _value = getattr(_args, _opt)
        result_dict.update({_opt: _value})
    return result_dict


def _merge_args(qCmd, parsed_args, _extra_values, value_specs):
    """Merge arguments from _extra_values into parsed_args.

    If an argument value are provided in both and it is a list,
    the values in _extra_values will be merged into parsed_args.

    @param parsed_args: the parsed args from known options
    @param _extra_values: the other parsed arguments in unknown parts
    @param values_specs: the unparsed unknown parts
    """
    temp_values = _extra_values.copy()
    for key, value in temp_values.items():
        if hasattr(parsed_args, key):
            arg_value = getattr(parsed_args, key)
            if arg_value is not None and value is not None:
                if isinstance(arg_value, list):
                    if value and isinstance(value, list):
                        if (not arg_value or
                                isinstance(arg_value[0], type(value[0]))):
                            arg_value.extend(value)
                            _extra_values.pop(key)


def update_dict(obj, dict, attributes):
    """Update dict with fields from obj.attributes.

    :param obj: the object updated into dict
    :param dict: the result dictionary
    :param attributes: a list of attributes belonging to obj
    """
    for attribute in attributes:
        if hasattr(obj, attribute) and getattr(obj, attribute) is not None:
            dict[attribute] = getattr(obj, attribute)


# cliff.command.Command is abstract class so that metaclass of
# subclass must be subclass of metaclass of all its base.
# otherwise metaclass conflict exception is raised.
class NeutronCommandMeta(abc.ABCMeta):
    def __new__(cls, name, bases, cls_dict):
        if 'log' not in cls_dict:
            cls_dict['log'] = logging.getLogger(
                cls_dict['__module__'] + '.' + name)
        return super(NeutronCommandMeta, cls).__new__(cls,
                                                      name, bases, cls_dict)


class NeutronCommand(command.Command, metaclass=NeutronCommandMeta):

    values_specs = []
    json_indent = None
    resource = None
    shadow_resource = None
    parent_id = None

    def run(self, parsed_args):
        self.log.debug('run(%s)', parsed_args)
        return super(NeutronCommand, self).run(parsed_args)

    @property
    def cmd_resource(self):
        if self.shadow_resource:
            return self.shadow_resource
        return self.resource

    def get_client(self):
        return self.app.client_manager.neutron

    def get_parser(self, prog_name):
        parser = super(NeutronCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--request-format',
            help=argparse.SUPPRESS,
            default='json',
            choices=['json', ], )
        parser.add_argument(
            '--request_format',
            choices=['json', ],
            help=argparse.SUPPRESS)

        return parser

    def cleanup_output_data(self, data):
        pass

    def format_output_data(self, data):
        # Modify data to make it more readable
        if self.resource in data:
            for k, v in data[self.resource].items():
                if isinstance(v, list):
                    value = '\n'.join(jsonutils.dumps(
                        i, indent=self.json_indent) if isinstance(i, dict)
                        else str(i) for i in v)
                    data[self.resource][k] = value
                elif isinstance(v, dict):
                    value = jsonutils.dumps(v, indent=self.json_indent)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''

    def add_known_arguments(self, parser):
        pass

    def set_extra_attrs(self, parsed_args):
        pass

    def args2body(self, parsed_args):
        return {}


class CreateCommand(NeutronCommand, show.ShowOne):
    """Create a resource for a given tenant."""

    log = None

    def get_parser(self, prog_name):
        parser = super(CreateCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='TENANT_ID',
            help=_('The owner tenant ID.'), )
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        self.add_known_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        self.set_extra_attrs(parsed_args)
        neutron_client = self.get_client()
        _extra_values = parse_args_to_dict(self.values_specs)
        _merge_args(self, parsed_args, _extra_values,
                    self.values_specs)
        body = self.args2body(parsed_args)
        body[self.resource].update(_extra_values)
        obj_creator = getattr(neutron_client,
                              "create_%s" % self.cmd_resource)
        if self.parent_id:
            data = obj_creator(self.parent_id, body)
        else:
            data = obj_creator(body)
        self.cleanup_output_data(data)
        if parsed_args.formatter == 'table':
            self.format_output_data(data)
        info = self.resource in data and data[self.resource] or None
        if info:
            if parsed_args.formatter == 'table':
                print(_('Created a new %s:') % self.resource,
                      file=self.app.stdout)
        else:
            info = {'': ''}
        return zip(*sorted(info.items()))


class UpdateCommand(NeutronCommand):
    """Update resource's information."""

    log = None
    allow_names = True
    help_resource = None

    def get_parser(self, prog_name):
        parser = super(UpdateCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = _('ID or name of %s to update.')
        else:
            help_str = _('ID of %s to update.')
        if not self.help_resource:
            self.help_resource = self.resource
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.help_resource)
        self.add_known_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        self.set_extra_attrs(parsed_args)
        neutron_client = self.get_client()
        _extra_values = parse_args_to_dict(self.values_specs)
        _merge_args(self, parsed_args, _extra_values,
                    self.values_specs)
        body = self.args2body(parsed_args)
        if self.resource in body:
            body[self.resource].update(_extra_values)
        else:
            body[self.resource] = _extra_values
        if not body[self.resource]:
            raise exceptions.CommandError(
                _("Must specify new values to update %s") %
                self.cmd_resource)
        if self.allow_names:
            _id = find_resourceid_by_name_or_id(
                neutron_client, self.resource, parsed_args.id,
                cmd_resource=self.cmd_resource, parent_id=self.parent_id)
        else:
            _id = find_resourceid_by_id(
                neutron_client, self.resource, parsed_args.id,
                self.cmd_resource, self.parent_id)
        obj_updater = getattr(neutron_client,
                              "update_%s" % self.cmd_resource)
        if self.parent_id:
            obj_updater(_id, self.parent_id, body)
        else:
            obj_updater(_id, body)
        print((_('Updated %(resource)s: %(id)s') %
               {'id': parsed_args.id, 'resource': self.resource}),
              file=self.app.stdout)
        return


class DeleteCommand(NeutronCommand):
    """Delete a given resource."""

    log = None
    allow_names = True
    help_resource = None
    bulk_delete = True

    def get_parser(self, prog_name):
        parser = super(DeleteCommand, self).get_parser(prog_name)
        if not self.help_resource:
            self.help_resource = self.resource
        if self.allow_names:
            help_str = _('ID(s) or name(s) of %s to delete.')
        else:
            help_str = _('ID(s) of %s to delete.')
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            nargs='+' if self.bulk_delete else 1,
            help=help_str % self.help_resource)
        self.add_known_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        self.set_extra_attrs(parsed_args)
        neutron_client = self.get_client()
        obj_deleter = getattr(neutron_client,
                              "delete_%s" % self.cmd_resource)

        if self.bulk_delete:
            self._bulk_delete(obj_deleter, neutron_client, parsed_args.id)
        else:
            self.delete_item(obj_deleter, neutron_client, parsed_args.id)
            print((_('Deleted %(resource)s: %(id)s')
                   % {'id': parsed_args.id,
                      'resource': self.resource}),
                  file=self.app.stdout)
        return

    def _bulk_delete(self, obj_deleter, neutron_client, parsed_args_ids):
        successful_delete = []
        non_existent = []
        multiple_ids = []
        for item_id in parsed_args_ids:
            try:
                self.delete_item(obj_deleter, neutron_client, item_id)
                successful_delete.append(item_id)
            except exceptions.NotFound:
                non_existent.append(item_id)
            except exceptions.NeutronClientNoUniqueMatch:
                multiple_ids.append(item_id)
        if successful_delete:
            print((_('Deleted %(resource)s(s): %(id)s'))
                  % {'id': ", ".join(successful_delete),
                     'resource': self.cmd_resource},
                  file=self.app.stdout)
        if non_existent or multiple_ids:
            err_msgs = []
            if non_existent:
                err_msgs.append((_("Unable to find %(resource)s(s) with id(s) "
                                   "'%(id)s'.") %
                                 {'resource': self.cmd_resource,
                                  'id': ", ".join(non_existent)}))
            if multiple_ids:
                err_msgs.append((_("Multiple %(resource)s(s) matches found "
                                   "for name(s) '%(id)s'. Please use an ID "
                                   "to be more specific.") %
                                 {'resource': self.cmd_resource,
                                  'id': ", ".join(multiple_ids)}))
            raise exceptions.NeutronCLIError(message='\n'.join(err_msgs))

    def delete_item(self, obj_deleter, neutron_client, item_id):
        if self.allow_names:
            params = {'cmd_resource': self.cmd_resource,
                      'parent_id': self.parent_id}
            _id = find_resourceid_by_name_or_id(neutron_client,
                                                self.resource,
                                                item_id,
                                                **params)
        else:
            _id = item_id

        if self.parent_id:
            obj_deleter(_id, self.parent_id)
        else:
            obj_deleter(_id)
        return


class ListCommand(NeutronCommand, lister.Lister):
    """List resources that belong to a given tenant."""

    log = None
    _formatters = {}
    list_columns = []
    unknown_parts_flag = True
    pagination_support = False
    sorting_support = False
    resource_plural = None

    # A list to define arguments for filtering by attribute value
    # CLI arguments are shown in the order of this list.
    # Each element must be either of a string of an attribute name
    # or a dict of a full attribute definitions whose format is:
    # {'name': attribute name, (mandatory)
    #  'help': help message for CLI (mandatory)
    #  'boolean': boolean parameter or not. (Default: False) (optional)
    #  'argparse_kwargs': a dict of parameters passed to
    #                     argparse add_argument()
    #                     (Default: {}) (optional)
    # }
    # For more details, see ListNetworks.filter_attrs.
    filter_attrs = []

    default_attr_defs = {
        'name': {
            'help': _("Filter %s according to their name."),
            'boolean': False,
        },
        'tenant_id': {
            'help': _('Filter %s belonging to the given tenant.'),
            'boolean': False,
        },
        'admin_state_up': {
            'help': _('Filter and list the %s whose administrative '
                      'state is active'),
            'boolean': True,
        },
    }

    def get_parser(self, prog_name):
        parser = super(ListCommand, self).get_parser(prog_name)
        add_show_list_common_argument(parser)
        if self.pagination_support:
            add_pagination_argument(parser)
        if self.sorting_support:
            add_sorting_argument(parser)
        self.add_known_arguments(parser)
        self.add_filtering_arguments(parser)
        return parser

    def add_filtering_arguments(self, parser):
        if not self.filter_attrs:
            return

        group_parser = parser.add_argument_group('filtering arguments')
        collection = self.resource_plural or '%ss' % self.resource
        for attr in self.filter_attrs:
            if isinstance(attr, str):
                # Use detail defined in default_attr_defs
                attr_name = attr
                attr_defs = self.default_attr_defs[attr]
            else:
                attr_name = attr['name']
                attr_defs = attr
            option_name = '--%s' % attr_name.replace('_', '-')
            params = attr_defs.get('argparse_kwargs', {})
            try:
                help_msg = attr_defs['help'] % collection
            except TypeError:
                help_msg = attr_defs['help']
            if attr_defs.get('boolean', False):
                add_arg_func = functools.partial(utils.add_boolean_argument,
                                                 group_parser)
            else:
                add_arg_func = group_parser.add_argument
            add_arg_func(option_name, help=help_msg, **params)

    def args2search_opts(self, parsed_args):
        search_opts = {}
        fields = parsed_args.fields
        if parsed_args.fields:
            search_opts.update({'fields': fields})
        if parsed_args.show_details:
            search_opts.update({'verbose': 'True'})
        filter_attrs = [field if isinstance(field, str) else field['name']
                        for field in self.filter_attrs]
        for attr in filter_attrs:
            val = getattr(parsed_args, attr, None)
            if attr in HYPHEN_OPTS:
                attr = attr.replace('_', '-')
            if val:
                search_opts[attr] = val
        return search_opts

    def call_server(self, neutron_client, search_opts, parsed_args):
        resource_plural = neutron_client.get_resource_plural(self.cmd_resource)
        obj_lister = getattr(neutron_client, "list_%s" % resource_plural)
        if self.parent_id:
            data = obj_lister(self.parent_id, **search_opts)
        else:
            data = obj_lister(**search_opts)
        return data

    def retrieve_list(self, parsed_args):
        """Retrieve a list of resources from Neutron server."""
        neutron_client = self.get_client()
        _extra_values = parse_args_to_dict(self.values_specs)
        _merge_args(self, parsed_args, _extra_values,
                    self.values_specs)
        search_opts = self.args2search_opts(parsed_args)
        search_opts.update(_extra_values)
        if self.pagination_support:
            page_size = parsed_args.page_size
            if page_size:
                search_opts.update({'limit': page_size})
        if self.sorting_support:
            keys = parsed_args.sort_key
            if keys:
                search_opts.update({'sort_key': keys})
            dirs = parsed_args.sort_dir
            len_diff = len(keys) - len(dirs)
            if len_diff > 0:
                dirs += ['asc'] * len_diff
            elif len_diff < 0:
                dirs = dirs[:len(keys)]
            if dirs:
                search_opts.update({'sort_dir': dirs})
        data = self.call_server(neutron_client, search_opts, parsed_args)
        collection = neutron_client.get_resource_plural(self.resource)
        return data.get(collection, [])

    def extend_list(self, data, parsed_args):
        """Update a retrieved list.

        This method provides a way to modify an original list returned from
        the neutron server. For example, you can add subnet cidr information
        to a network list.
        """
        pass

    def setup_columns(self, info, parsed_args):
        _columns = len(info) > 0 and sorted(info[0].keys()) or []
        if not _columns:
            # clean the parsed_args.columns so that cliff will not break
            parsed_args.columns = []
        elif parsed_args.columns:
            _columns = [x for x in parsed_args.columns if x in _columns]
        elif self.list_columns:
            # if no -c(s) by user and list_columns, we use columns in
            # both list_columns and returned resource.
            # Also Keep their order the same as in list_columns
            _columns = self._setup_columns_with_tenant_id(self.list_columns,
                                                          _columns)

        if parsed_args.formatter == 'table':
            formatters = self._formatters
        elif (parsed_args.formatter == 'csv' and
              hasattr(self, '_formatters_csv')):
            formatters = self._formatters_csv
        else:
            # For other formatters, we use raw value returned from neutron
            formatters = {}

        return (_columns, (utils.get_item_properties(
            s, _columns, formatters=formatters, )
            for s in info), )

    def _setup_columns_with_tenant_id(self, display_columns, avail_columns):
        _columns = [x for x in display_columns if x in avail_columns]
        if 'tenant_id' in display_columns:
            return _columns
        if 'tenant_id' not in avail_columns:
            return _columns
        if not self.is_admin_role():
            return _columns
        try:
            pos_id = _columns.index('id')
        except ValueError:
            pos_id = 0
        try:
            pos_name = _columns.index('name')
        except ValueError:
            pos_name = 0
        _columns.insert(max(pos_id, pos_name) + 1, 'tenant_id')
        return _columns

    def is_admin_role(self):
        client = self.get_client()
        auth_ref = client.httpclient.get_auth_ref()
        if not auth_ref:
            return False
        return 'admin' in auth_ref.role_names

    def take_action(self, parsed_args):
        self.set_extra_attrs(parsed_args)
        data = self.retrieve_list(parsed_args)
        self.extend_list(data, parsed_args)
        return self.setup_columns(data, parsed_args)


class ShowCommand(NeutronCommand, show.ShowOne):
    """Show information of a given resource."""

    log = None
    allow_names = True
    help_resource = None

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        add_show_list_common_argument(parser)
        if self.allow_names:
            help_str = _('ID or name of %s to look up.')
        else:
            help_str = _('ID of %s to look up.')
        if not self.help_resource:
            self.help_resource = self.resource
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.help_resource)
        self.add_known_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        self.set_extra_attrs(parsed_args)
        neutron_client = self.get_client()

        params = {}
        if parsed_args.show_details:
            params = {'verbose': 'True'}
        if parsed_args.fields:
            params = {'fields': parsed_args.fields}
        if self.allow_names:
            _id = find_resourceid_by_name_or_id(neutron_client,
                                                self.resource,
                                                parsed_args.id,
                                                cmd_resource=self.cmd_resource,
                                                parent_id=self.parent_id)
        else:
            _id = parsed_args.id

        obj_shower = getattr(neutron_client, "show_%s" % self.cmd_resource)
        if self.parent_id:
            data = obj_shower(_id, self.parent_id, **params)
        else:
            data = obj_shower(_id, **params)
        self.cleanup_output_data(data)
        if parsed_args.formatter == 'table':
            self.format_output_data(data)
        resource = data[self.resource]
        if self.resource in data:
            return zip(*sorted(resource.items()))
        else:
            return None
