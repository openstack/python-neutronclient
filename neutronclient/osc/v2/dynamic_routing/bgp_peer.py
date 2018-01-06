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
from osc_lib import utils
from osc_lib.utils import columns as column_util

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils as nc_utils
from neutronclient.osc import utils as nc_osc_utils
from neutronclient.osc.v2.dynamic_routing import constants


def _get_attrs(client_manager, parsed_args):
    attrs = {}

    # Validate password
    if 'auth_type' in parsed_args:
        if parsed_args.auth_type != 'none':
            if 'password' not in parsed_args or parsed_args.password is None:
                raise exceptions.CommandError(_('Must provide password if '
                                                'auth-type is specified.'))
        if (
            parsed_args.auth_type == 'none' and
            parsed_args.password is not None
        ):
            raise exceptions.CommandError(_('Must provide auth-type if '
                                            'password is specified.'))
        attrs['auth_type'] = parsed_args.auth_type

    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if 'remote_as' in parsed_args:
        attrs['remote_as'] = parsed_args.remote_as
    if 'peer_ip' in parsed_args:
        attrs['peer_ip'] = parsed_args.peer_ip
    if 'password' in parsed_args:
        attrs['password'] = parsed_args.password

    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = nc_osc_utils.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id
    return attrs


class CreateBgpPeer(command.ShowOne):
    _description = _("Create a BGP peer")

    def get_parser(self, prog_name):
        parser = super(CreateBgpPeer, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("Name of the BGP peer to create"))
        parser.add_argument(
            '--peer-ip',
            metavar='<peer-ip-address>',
            required=True,
            help=_("Peer IP address"))
        parser.add_argument(
            '--remote-as',
            required=True,
            metavar='<peer-remote-as>',
            help=_("Peer AS number. (Integer in [%(min_val)s, %(max_val)s] "
                   "is allowed)") % {'min_val': constants.MIN_AS_NUM,
                                     'max_val': constants.MAX_AS_NUM})
        parser.add_argument(
            '--auth-type',
            metavar='<peer-auth-type>',
            choices=['none', 'md5'],
            type=nc_utils.convert_to_lowercase,
            default='none',
            help=_("Authentication algorithm. Supported algorithms: "
                   "none (default), md5"))
        parser.add_argument(
            '--password',
            metavar='<auth-password>',
            help=_("Authentication password"))
        nc_osc_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        body = {constants.BGP_PEER: attrs}
        obj = client.create_bgp_peer(body)[constants.BGP_PEER]
        columns, display_columns = column_util.get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteBgpPeer(command.Command):
    _description = _("Delete a BGP peer")

    def get_parser(self, prog_name):
        parser = super(DeleteBgpPeer, self).get_parser(prog_name)
        parser.add_argument(
            'bgp_peer',
            metavar="<bgp-peer>",
            help=_("BGP peer to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        id = client.find_resource(constants.BGP_PEER,
                                  parsed_args.bgp_peer)['id']
        client.delete_bgp_peer(id)


class ListBgpPeer(command.Lister):
    _description = _("List BGP peers")

    def take_action(self, parsed_args):
        data = self.app.client_manager.neutronclient.list_bgp_peers()
        headers = ('ID', 'Name', 'Peer IP', 'Remote AS')
        columns = ('id', 'name', 'peer_ip', 'remote_as')
        return (headers,
                (utils.get_dict_properties(
                    s, columns,
                ) for s in data[constants.BGP_PEERS]))


class SetBgpPeer(command.Command):
    _description = _("Update a BGP peer")
    resource = constants.BGP_PEER

    def get_parser(self, prog_name):
        parser = super(SetBgpPeer, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            help=_("Updated name of the BGP peer"))
        parser.add_argument(
            '--password',
            metavar='<auth-password>',
            help=_("Updated authentication password"))
        parser.add_argument(
            'bgp_peer',
            metavar="<bgp-peer>",
            help=_("BGP peer to update (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        id = client.find_resource(constants.BGP_PEER,
                                  parsed_args.bgp_peer)['id']
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        body = {}
        body[constants.BGP_PEER] = attrs
        client.update_bgp_peer(id, body)


class ShowBgpPeer(command.ShowOne):
    _description = _("Show information for a BGP peer")

    def get_parser(self, prog_name):
        parser = super(ShowBgpPeer, self).get_parser(prog_name)
        parser.add_argument(
            'bgp_peer',
            metavar="<bgp-peer>",
            help=_("BGP peer to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.neutronclient
        id = client.find_resource(constants.BGP_PEER,
                                  parsed_args.bgp_peer)['id']
        obj = client.show_bgp_peer(id)[constants.BGP_PEER]
        columns, display_columns = column_util.get_columns(obj)
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data
