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
    ('encapsulation_mode', 'Encapsulation Mode', column_util.LIST_BOTH),
    ('transform_protocol', 'Transform Protocol', column_util.LIST_BOTH),
    ('encryption_algorithm', 'Encryption Algorithm', column_util.LIST_BOTH),
    ('pfs', 'Perfect Forward Secrecy (PFS)', column_util.LIST_LONG_ONLY),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('lifetime', 'Lifetime', column_util.LIST_LONG_ONLY),
)

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'auth_algorithm': 'Authentication Algorithm',
    'encapsulation_mode': 'Encapsulation Mode',
    'transform_protocol': 'Transform Protocol',
    'encryption_algorithm': 'Encryption Algorithm',
    'pfs': 'Perfect Forward Secrecy (PFS)',
    'lifetime': 'Lifetime',
    'description': 'Description',
    'project_id': 'Project',
}


def _convert_to_lowercase(string):
    return string.lower()


def _get_common_parser(parser):
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_('Description of the IPsec policy'))
    parser.add_argument(
        '--auth-algorithm',
        choices=['sha1', 'sha256', 'sha384', 'sha512'],
        type=_convert_to_lowercase,
        help=_('Authentication algorithm for IPsec policy'))
    parser.add_argument(
        '--encapsulation-mode',
        choices=['tunnel', 'transport'],
        type=_convert_to_lowercase,
        help=_('Encapsulation mode for IPsec policy'))
    parser.add_argument(
        '--encryption-algorithm',
        choices=['3des', 'aes-128', 'aes-192', 'aes-256'],
        type=_convert_to_lowercase,
        help=_('Encryption algorithm for IPsec policy'))
    parser.add_argument(
        '--lifetime',
        metavar="units=UNITS,value=VALUE",
        type=nc_utils.str2dict_type(optional_keys=['units', 'value']),
        help=vpn_utils.lifetime_help("IPsec"))
    parser.add_argument(
        '--pfs',
        choices=['group2', 'group5', 'group14'],
        type=_convert_to_lowercase,
        help=_('Perfect Forward Secrecy for IPsec policy'))
    parser.add_argument(
        '--transform-protocol',
        type=_convert_to_lowercase,
        choices=['esp', 'ah', 'ah-esp'],
        help=_('Transform protocol for IPsec policy'))


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
        attrs['description'] = str(parsed_args.description)
    if parsed_args.auth_algorithm:
        attrs['auth_algorithm'] = parsed_args.auth_algorithm
    if parsed_args.encapsulation_mode:
        attrs['encapsulation_mode'] = parsed_args.encapsulation_mode
    if parsed_args.transform_protocol:
        attrs['transform_protocol'] = parsed_args.transform_protocol
    if parsed_args.encryption_algorithm:
        attrs['encryption_algorithm'] = parsed_args.encryption_algorithm
    if parsed_args.pfs:
        attrs['pfs'] = parsed_args.pfs
    if parsed_args.lifetime:
        vpn_utils.validate_lifetime_dict(parsed_args.lifetime)
        attrs['lifetime'] = parsed_args.lifetime
    return attrs


class CreateIPsecPolicy(command.ShowOne):
    _description = _("Create an IPsec policy")

    def get_parser(self, prog_name):
        parser = super(CreateIPsecPolicy, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the IPsec policy'))
        osc_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        obj = client.create_vpn_ipsec_policy(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id',
                                  'phase1_negotiation_mode', 'units', 'value'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteIPsecPolicy(command.Command):
    _description = _("Delete IPsec policy(policies)")

    def get_parser(self, prog_name):
        parser = super(DeleteIPsecPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'ipsecpolicy',
            metavar='<ipsec-policy>',
            nargs='+',
            help=_('ipsec policy to delete (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for ipsec in parsed_args.ipsecpolicy:
            try:
                ipsec_id = client.find_vpn_ipsec_policy(
                    ipsec, ignore_missing=False)['id']
                client.delete_vpn_ipsec_policy(ipsec_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete IPsec policy with "
                            "name or ID '%(ipsecpolicy)s': %(e)s"),
                          {'ipsecpolicy': ipsec, 'e': e})

        if result > 0:
            total = len(parsed_args.ipsecpolicy)
            msg = (_("%(result)s of %(total)s IPsec policy failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListIPsecPolicy(command.Lister):
    _description = _("List IPsec policies that belong to a given project")

    def get_parser(self, prog_name):
        parser = super(ListIPsecPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.vpn_ipsec_policies()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(s, columns) for s in obj))


class SetIPsecPolicy(command.Command):
    _description = _("Set IPsec policy properties")

    def get_parser(self, prog_name):
        parser = super(SetIPsecPolicy, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the IPsec policy'))
        parser.add_argument(
            'ipsecpolicy',
            metavar='<ipsec-policy>',
            help=_('IPsec policy to set (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager,
                                  parsed_args, is_create=False)
        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        ipsec_id = client.find_vpn_ipsec_policy(
            parsed_args.ipsecpolicy, ignore_missing=False)['id']
        try:
            client.update_vpn_ipsec_policy(ipsec_id, **attrs)
        except Exception as e:
            msg = (_("Failed to set IPsec policy '%(ipsec)s': %(e)s")
                   % {'ipsec': parsed_args.ipsecpolicy, 'e': e})
            raise exceptions.CommandError(msg)


class ShowIPsecPolicy(command.ShowOne):
    _description = _("Display IPsec policy details")

    def get_parser(self, prog_name):
        parser = super(ShowIPsecPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'ipsecpolicy',
            metavar='<ipsec-policy>',
            help=_('IPsec policy to display (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        ipsec_id = client.find_vpn_ipsec_policy(
            parsed_args.ipsecpolicy, ignore_missing=False)['id']
        obj = client.get_vpn_ipsec_policy(ipsec_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id',
                                  'phase1_negotiation_mode', 'units', 'value'])
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)
