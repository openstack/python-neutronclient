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

"""
Command-line interface to the Quantum APIs
"""

import argparse
import gettext
import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from quantumclient.common import clientmanager
from quantumclient.common import exceptions as exc
from quantumclient.common import utils


VERSION = '2.0'
QUANTUM_API_VERSION = '2.0'


def env(*_vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in _vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


COMMAND_V2 = {
    'net-list': utils.import_class(
        'quantumclient.quantum.v2_0.network.ListNetwork'),
    'net-external-list': utils.import_class(
        'quantumclient.quantum.v2_0.network.ListExternalNetwork'),
    'net-show': utils.import_class(
        'quantumclient.quantum.v2_0.network.ShowNetwork'),
    'net-create': utils.import_class(
        'quantumclient.quantum.v2_0.network.CreateNetwork'),
    'net-delete': utils.import_class(
        'quantumclient.quantum.v2_0.network.DeleteNetwork'),
    'net-update': utils.import_class(
        'quantumclient.quantum.v2_0.network.UpdateNetwork'),
    'subnet-list': utils.import_class(
        'quantumclient.quantum.v2_0.subnet.ListSubnet'),
    'subnet-show': utils.import_class(
        'quantumclient.quantum.v2_0.subnet.ShowSubnet'),
    'subnet-create': utils.import_class(
        'quantumclient.quantum.v2_0.subnet.CreateSubnet'),
    'subnet-delete': utils.import_class(
        'quantumclient.quantum.v2_0.subnet.DeleteSubnet'),
    'subnet-update': utils.import_class(
        'quantumclient.quantum.v2_0.subnet.UpdateSubnet'),
    'port-list': utils.import_class(
        'quantumclient.quantum.v2_0.port.ListPort'),
    'port-show': utils.import_class(
        'quantumclient.quantum.v2_0.port.ShowPort'),
    'port-create': utils.import_class(
        'quantumclient.quantum.v2_0.port.CreatePort'),
    'port-delete': utils.import_class(
        'quantumclient.quantum.v2_0.port.DeletePort'),
    'port-update': utils.import_class(
        'quantumclient.quantum.v2_0.port.UpdatePort'),
    'quota-list': utils.import_class(
        'quantumclient.quantum.v2_0.quota.ListQuota'),
    'quota-show': utils.import_class(
        'quantumclient.quantum.v2_0.quota.ShowQuota'),
    'quota-delete': utils.import_class(
        'quantumclient.quantum.v2_0.quota.DeleteQuota'),
    'quota-update': utils.import_class(
        'quantumclient.quantum.v2_0.quota.UpdateQuota'),
    'ext-list': utils.import_class(
        'quantumclient.quantum.v2_0.extension.ListExt'),
    'ext-show': utils.import_class(
        'quantumclient.quantum.v2_0.extension.ShowExt'),
    'router-list': utils.import_class(
        'quantumclient.quantum.v2_0.router.ListRouter'),
    'router-port-list': utils.import_class(
        'quantumclient.quantum.v2_0.port.ListRouterPort'),
    'router-show': utils.import_class(
        'quantumclient.quantum.v2_0.router.ShowRouter'),
    'router-create': utils.import_class(
        'quantumclient.quantum.v2_0.router.CreateRouter'),
    'router-delete': utils.import_class(
        'quantumclient.quantum.v2_0.router.DeleteRouter'),
    'router-update': utils.import_class(
        'quantumclient.quantum.v2_0.router.UpdateRouter'),
    'router-interface-add': utils.import_class(
        'quantumclient.quantum.v2_0.router.AddInterfaceRouter'),
    'router-interface-delete': utils.import_class(
        'quantumclient.quantum.v2_0.router.RemoveInterfaceRouter'),
    'router-gateway-set': utils.import_class(
        'quantumclient.quantum.v2_0.router.SetGatewayRouter'),
    'router-gateway-clear': utils.import_class(
        'quantumclient.quantum.v2_0.router.RemoveGatewayRouter'),
    'floatingip-list': utils.import_class(
        'quantumclient.quantum.v2_0.floatingip.ListFloatingIP'),
    'floatingip-show': utils.import_class(
        'quantumclient.quantum.v2_0.floatingip.ShowFloatingIP'),
    'floatingip-create': utils.import_class(
        'quantumclient.quantum.v2_0.floatingip.CreateFloatingIP'),
    'floatingip-delete': utils.import_class(
        'quantumclient.quantum.v2_0.floatingip.DeleteFloatingIP'),
    'floatingip-associate': utils.import_class(
        'quantumclient.quantum.v2_0.floatingip.AssociateFloatingIP'),
    'floatingip-disassociate': utils.import_class(
        'quantumclient.quantum.v2_0.floatingip.DisassociateFloatingIP'),
    'security-group-list': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.ListSecurityGroup'),
    'security-group-show': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.ShowSecurityGroup'),
    'security-group-create': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.CreateSecurityGroup'),
    'security-group-delete': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.DeleteSecurityGroup'),
    'security-group-rule-list': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.ListSecurityGroupRule'),
    'security-group-rule-show': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.ShowSecurityGroupRule'),
    'security-group-rule-create': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.CreateSecurityGroupRule'),
    'security-group-rule-delete': utils.import_class(
        'quantumclient.quantum.v2_0.securitygroup.DeleteSecurityGroupRule'),
    'lb-vip-list': utils.import_class(
        'quantumclient.quantum.v2_0.lb.vip.ListVip'),
    'lb-vip-show': utils.import_class(
        'quantumclient.quantum.v2_0.lb.vip.ShowVip'),
    'lb-vip-create': utils.import_class(
        'quantumclient.quantum.v2_0.lb.vip.CreateVip'),
    'lb-vip-update': utils.import_class(
        'quantumclient.quantum.v2_0.lb.vip.UpdateVip'),
    'lb-vip-delete': utils.import_class(
        'quantumclient.quantum.v2_0.lb.vip.DeleteVip'),
    'lb-pool-list': utils.import_class(
        'quantumclient.quantum.v2_0.lb.pool.ListPool'),
    'lb-pool-show': utils.import_class(
        'quantumclient.quantum.v2_0.lb.pool.ShowPool'),
    'lb-pool-create': utils.import_class(
        'quantumclient.quantum.v2_0.lb.pool.CreatePool'),
    'lb-pool-update': utils.import_class(
        'quantumclient.quantum.v2_0.lb.pool.UpdatePool'),
    'lb-pool-delete': utils.import_class(
        'quantumclient.quantum.v2_0.lb.pool.DeletePool'),
    'lb-pool-stats': utils.import_class(
        'quantumclient.quantum.v2_0.lb.pool.RetrievePoolStats'),
    'lb-member-list': utils.import_class(
        'quantumclient.quantum.v2_0.lb.member.ListMember'),
    'lb-member-show': utils.import_class(
        'quantumclient.quantum.v2_0.lb.member.ShowMember'),
    'lb-member-create': utils.import_class(
        'quantumclient.quantum.v2_0.lb.member.CreateMember'),
    'lb-member-update': utils.import_class(
        'quantumclient.quantum.v2_0.lb.member.UpdateMember'),
    'lb-member-delete': utils.import_class(
        'quantumclient.quantum.v2_0.lb.member.DeleteMember'),
    'lb-healthmonitor-list': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor.ListHealthMonitor'),
    'lb-healthmonitor-show': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor.ShowHealthMonitor'),
    'lb-healthmonitor-create': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor.CreateHealthMonitor'),
    'lb-healthmonitor-update': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor.UpdateHealthMonitor'),
    'lb-healthmonitor-delete': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor.DeleteHealthMonitor'),
    'lb-healthmonitor-associate': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor.AssociateHealthMonitor'),
    'lb-healthmonitor-disassociate': utils.import_class(
        'quantumclient.quantum.v2_0.lb.healthmonitor'
        '.DisassociateHealthMonitor'),
}

COMMANDS = {'2.0': COMMAND_V2}


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v%s:\n' % app.api_version)
        command_manager = app.command_manager
        for name, ep in sorted(command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)
        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))
        sys.exit(0)


class QuantumShell(App):

    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    DEBUG_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
    log = logging.getLogger(__name__)

    def __init__(self, apiversion):
        super(QuantumShell, self).__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=CommandManager('quantum.cli'), )
        self.commands = COMMANDS
        for k, v in self.commands[apiversion].items():
            self.command_manager.add_command(k, v)

        # This is instantiated in initialize_app() only when using
        # password flow auth
        self.auth_client = None
        self.api_version = apiversion

    def build_option_parser(self, description, version):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        """
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False, )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version), )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.', )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors', )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="show this help message and exit", )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='show tracebacks on errors', )
        # Global arguments
        parser.add_argument(
            '--os-auth-strategy', metavar='<auth-strategy>',
            default=env('OS_AUTH_STRATEGY', default='keystone'),
            help='Authentication strategy (Env: OS_AUTH_STRATEGY'
            ', default keystone). For now, any other value will'
            ' disable the authentication')
        parser.add_argument(
            '--os_auth_strategy',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-auth-url', metavar='<auth-url>',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)')
        parser.add_argument(
            '--os_auth_url',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-tenant-name', metavar='<auth-tenant-name>',
            default=env('OS_TENANT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)')
        parser.add_argument(
            '--os_tenant_name',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-username', metavar='<auth-username>',
            default=utils.env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)')
        parser.add_argument(
            '--os_username',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-password', metavar='<auth-password>',
            default=utils.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)')
        parser.add_argument(
            '--os_password',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-region-name', metavar='<auth-region-name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')
        parser.add_argument(
            '--os_region_name',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-token', metavar='<token>',
            default=env('OS_TOKEN'),
            help='Defaults to env[OS_TOKEN]')
        parser.add_argument(
            '--os_token',
            help=argparse.SUPPRESS)

        parser.add_argument(
            '--os-url', metavar='<url>',
            default=env('OS_URL'),
            help='Defaults to env[OS_URL]')
        parser.add_argument(
            '--os_url',
            help=argparse.SUPPRESS)

        return parser

    def _bash_completion(self):
        """
        Prints all of the commands and options to stdout so that the
        quantum's bash-completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for option, _action in self.parser._option_string_actions.items():
            options.add(option)
        for command_name, command in self.command_manager:
            commands.add(command_name)
            cmd_factory = command.load()
            cmd = cmd_factory(self, None)
            cmd_parser = cmd.get_parser('')
            for option, _action in cmd_parser._option_string_actions.items():
                options.add(option)
        print ' '.join(commands | options)

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            index = 0
            command_pos = -1
            help_pos = -1
            help_command_pos = -1
            for arg in argv:
                if arg == 'bash-completion':
                    self._bash_completion()
                    return 0
                if arg in self.commands[self.api_version]:
                    if command_pos == -1:
                        command_pos = index
                elif arg in ('-h', '--help'):
                    if help_pos == -1:
                        help_pos = index
                elif arg == 'help':
                    if help_command_pos == -1:
                        help_command_pos = index
                index = index + 1
            if command_pos > -1 and help_pos > command_pos:
                argv = ['help', argv[command_pos]]
            if help_command_pos > -1 and command_pos == -1:
                argv[help_command_pos] = '--help'
            self.options, remainder = self.parser.parse_known_args(argv)
            self.configure_logging()
            self.interactive_mode = not remainder
            self.initialize_app(remainder)
        except Exception as err:
            if self.options.debug:
                self.log.exception(err)
                raise
            else:
                self.log.error(err)
            return 1
        result = 1
        if self.interactive_mode:
            _argv = [sys.argv[0]]
            sys.argv = _argv
            result = self.interact()
        else:
            result = self.run_subcommand(remainder)
        return result

    def run_subcommand(self, argv):
        subcommand = self.command_manager.find_command(argv)
        cmd_factory, cmd_name, sub_argv = subcommand
        cmd = cmd_factory(self, self.options)
        err = None
        result = 1
        try:
            self.prepare_to_run_command(cmd)
            full_name = (cmd_name
                         if self.interactive_mode
                         else ' '.join([self.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            known_args, values_specs = cmd_parser.parse_known_args(sub_argv)
            cmd.values_specs = values_specs
            result = cmd.run(known_args)
        except Exception as err:
            if self.options.debug:
                self.log.exception(err)
            else:
                self.log.error(err)
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    self.log.exception(err2)
                else:
                    self.log.error('Could not clean up: %s', err2)
            if self.options.debug:
                raise
        else:
            try:
                self.clean_up(cmd, result, None)
            except Exception as err3:
                if self.options.debug:
                    self.log.exception(err3)
                else:
                    self.log.error('Could not clean up: %s', err3)
        return result

    def authenticate_user(self):
        """Make sure the user has provided all of the authentication
        info we need.
        """
        if self.options.os_auth_strategy == 'keystone':
            if self.options.os_token or self.options.os_url:
                # Token flow auth takes priority
                if not self.options.os_token:
                    raise exc.CommandError(
                        "You must provide a token via"
                        " either --os-token or env[OS_TOKEN]")

                if not self.options.os_url:
                    raise exc.CommandError(
                        "You must provide a service URL via"
                        " either --os-url or env[OS_URL]")

            else:
                # Validate password flow auth
                if not self.options.os_username:
                    raise exc.CommandError(
                        "You must provide a username via"
                        " either --os-username or env[OS_USERNAME]")

                if not self.options.os_password:
                    raise exc.CommandError(
                        "You must provide a password via"
                        " either --os-password or env[OS_PASSWORD]")

                if not (self.options.os_tenant_name):
                    raise exc.CommandError(
                        "You must provide a tenant_name via"
                        " either --os-tenant-name or via env[OS_TENANT_NAME]")

                if not self.options.os_auth_url:
                    raise exc.CommandError(
                        "You must provide an auth url via"
                        " either --os-auth-url or via env[OS_AUTH_URL]")
        else:   # not keystone
            if not self.options.os_url:
                raise exc.CommandError(
                    "You must provide a service URL via"
                    " either --os-url or env[OS_URL]")

        self.client_manager = clientmanager.ClientManager(
            token=self.options.os_token,
            url=self.options.os_url,
            auth_url=self.options.os_auth_url,
            tenant_name=self.options.os_tenant_name,
            username=self.options.os_username,
            password=self.options.os_password,
            region_name=self.options.os_region_name,
            api_version=self.api_version,
            auth_strategy=self.options.os_auth_strategy, )
        return

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        """

        super(QuantumShell, self).initialize_app(argv)

        self.api_version = {'network': self.api_version}

        # If the user is not asking for help, make sure they
        # have given us auth.
        cmd_name = None
        if argv:
            cmd_info = self.command_manager.find_command(argv)
            cmd_factory, cmd_name, sub_argv = cmd_info
        if self.interactive_mode or cmd_name != 'help':
            self.authenticate_user()

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

    def configure_logging(self):
        """Create logging handlers for any log output.
        """
        root_logger = logging.getLogger('')

        # Set up logging to a file
        root_logger.setLevel(logging.DEBUG)

        # Send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        console.setLevel(console_level)
        if logging.DEBUG == console_level:
            formatter = logging.Formatter(self.DEBUG_MESSAGE_FORMAT)
        else:
            formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)
        return


def main(argv=sys.argv[1:]):
    gettext.install('quantumclient', unicode=1)
    try:
        return QuantumShell(QUANTUM_API_VERSION).run(argv)
    except exc.QuantumClientException:
        return 1
    except Exception as e:
        print e
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
