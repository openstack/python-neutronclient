#    Copyright 2017 FUJITSU LIMITED
#    All Rights Reserved.
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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util
from oslo_log import log as logging

from neutronclient._i18n import _
from neutronclient.common import utils as nc_utils
from neutronclient.osc import utils as osc_utils
from neutronclient.osc.v2.vpnaas import utils as vpn_utils


LOG = logging.getLogger(__name__)

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('auth_algorithm', 'Authentication Algorithm', column_util.LIST_BOTH),
    ('encryption_algorithm', 'Encryption Algorithm', column_util.LIST_BOTH),
    ('ike_version', 'IKE Version', column_util.LIST_BOTH),
    ('pfs', 'Perfect Forward Secrecy (PFS)', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('phase1_negotiation_mode', 'Phase1 Negotiation Mode',
        column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('lifetime', 'Lifetime', column_util.LIST_LONG_ONLY),
)

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'auth_algorithm': 'Authentication Algorithm',
    'encryption_algorithm': 'Encryption Algorithm',
    'ike_version': 'IKE Version',
    'pfs': 'Perfect Forward Secrecy (PFS)',
    'phase1_negotiation_mode': 'Phase1 Negotiation Mode',
    'lifetime': 'Lifetime',
    'description': 'Description',
    'tenant_id': 'Project',
    'project_id': 'Project',
}


def _convert_to_lowercase(string):
    return string.lower()


def _get_common_parser(parser):
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_('Description of the IKE policy'))
    parser.add_argument(
        '--auth-algorithm',
        choices=['sha1', 'sha256', 'sha384', 'sha512'],
        type=_convert_to_lowercase,
        help=_('Authentication algorithm'))
    parser.add_argument(
        '--encryption-algorithm',
        choices=['aes-128', '3des', 'aes-192', 'aes-256'],
        type=_convert_to_lowercase,
        help=_('Encryption algorithm'))
    parser.add_argument(
        '--phase1-negotiation-mode',
        choices=['main', 'aggressive'],
        type=_convert_to_lowercase,
        help=_('IKE Phase1 negotiation mode'))
    parser.add_argument(
        '--ike-version',
        choices=['v1', 'v2'],
        type=_convert_to_lowercase,
        help=_('IKE version for the policy'))
    parser.add_argument(
        '--pfs',
        choices=['group5', 'group2', 'group14'],
        type=_convert_to_lowercase,
        help=_('Perfect Forward Secrecy'))
    parser.add_argument(
        '--lifetime',
        metavar="units=UNITS,value=VALUE",
        type=nc_utils.str2dict_type(optional_keys=['units', 'value']),
        help=vpn_utils.lifetime_help("IKE"))
    return parser


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['project_id'] = osc_utils.find_project(
                client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
    if parsed_args.description:
        attrs['description'] = parsed_args.description
    if parsed_args.auth_algorithm:
        attrs['auth_algorithm'] = parsed_args.auth_algorithm
    if parsed_args.encryption_algorithm:
        attrs['encryption_algorithm'] = parsed_args.encryption_algorithm
    if parsed_args.phase1_negotiation_mode:
        attrs['phase1_negotiation_mode'] = parsed_args.phase1_negotiation_mode
    if parsed_args.ike_version:
        attrs['ike_version'] = parsed_args.ike_version
    if parsed_args.pfs:
        attrs['pfs'] = parsed_args.pfs
    if parsed_args.lifetime:
        vpn_utils.validate_lifetime_dict(parsed_args.lifetime)
        attrs['lifetime'] = parsed_args.lifetime
    return attrs


class CreateIKEPolicy(command.ShowOne):
    _description = _("Create an IKE policy")

    def get_parser(self, prog_name):
        parser = super(CreateIKEPolicy, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the IKE policy'))
        osc_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        obj = client.create_vpn_ike_policy(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id', 'units', 'value'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteIKEPolicy(command.Command):
    _description = _("Delete IKE policy (policies)")

    def get_parser(self, prog_name):
        parser = super(DeleteIKEPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'ikepolicy',
            metavar='<ike-policy>',
            nargs='+',
            help=_('IKE policy to delete (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for ike in parsed_args.ikepolicy:
            try:
                ike_id = client.find_vpn_ike_policy(ike,
                                                    ignore_missing=False)['id']
                client.delete_vpn_ike_policy(ike_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete IKE policy with "
                            "name or ID '%(ikepolicy)s': %(e)s"),
                          {'ikepolicy': ike, 'e': e})

        if result > 0:
            total = len(parsed_args.ikepolicy)
            msg = (_("%(result)s of %(total)s IKE policy failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListIKEPolicy(command.Lister):
    _description = _("List IKE policies that belong to a given project")

    def get_parser(self, prog_name):
        parser = super(ListIKEPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.vpn_ike_policies()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(s, columns) for s in obj))


class SetIKEPolicy(command.Command):
    _description = _("Set IKE policy properties")

    def get_parser(self, prog_name):
        parser = super(SetIKEPolicy, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the IKE policy'))
        parser.add_argument(
            'ikepolicy',
            metavar='<ike-policy>',
            help=_('IKE policy to set (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager,
                                  parsed_args, is_create=False)
        if parsed_args.name:
            attrs['name'] = parsed_args.name
        ike_id = client.find_vpn_ike_policy(parsed_args.ikepolicy,
                                            ignore_missing=False)['id']
        try:
            client.update_vpn_ike_policy(ike_id, **attrs)
        except Exception as e:
            msg = (_("Failed to set IKE policy '%(ike)s': %(e)s")
                   % {'ike': parsed_args.ikepolicy, 'e': e})
            raise exceptions.CommandError(msg)


class ShowIKEPolicy(command.ShowOne):
    _description = _("Display IKE policy details")

    def get_parser(self, prog_name):
        parser = super(ShowIKEPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'ikepolicy',
            metavar='<ike-policy>',
            help=_('IKE policy to display (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        ike_id = client.find_vpn_ike_policy(parsed_args.ikepolicy,
                                            ignore_missing=False)['id']
        obj = client.get_vpn_ike_policy(ike_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id', 'units', 'value'])
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)
