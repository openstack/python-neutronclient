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
import itertools
import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from quantumclient.common import clientmanager
from quantumclient.common import exceptions as exc
from quantumclient.common import utils


gettext.install('quantum', unicode=1)
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
}

COMMANDS = {'2.0': COMMAND_V2}


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v%s:\n' % app.api_version)
        command_manager = app.command_manager
        for name, ep in sorted(command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            app.stdout.write('  %-13s  %s\n' % (name, one_liner))
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
        for k, v in COMMANDS[apiversion].items():
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
            '--os_auth_strategy', metavar='<auth_strategy>',
            default=env('OS_AUTH_STRATEGY', default='keystone'),
            help='Authentication strategy (Env: OS_AUTH_STRATEGY'
            ', default keystone). For now, any other value will'
            ' disable the authentication')

        parser.add_argument(
            '--os_auth_url', metavar='<auth_url>',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)')

        parser.add_argument(
            '--os_tenant_name', metavar='<auth_tenant_name>',
            default=env('OS_TENANT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)')

        parser.add_argument(
            '--os_username', metavar='<auth_username>',
            default=utils.env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)')

        parser.add_argument(
            '--os_password', metavar='<auth_password>',
            default=utils.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)')

        parser.add_argument(
            '--os_region_name', metavar='<auth_region_name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')

        parser.add_argument(
            '--os_token', metavar='<token>',
            default=env('OS_TOKEN'),
            help='Defaults to env[OS_TOKEN]')

        parser.add_argument(
            '--os_url', metavar='<url>',
            default=env('OS_URL'),
            help='Defaults to env[OS_URL]')

        return parser

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            index = 0
            command_pos = -1
            help_pos = -1
            for arg in argv:
                if arg in COMMANDS[self.api_version]:
                    if command_pos == -1:
                        command_pos = index
                elif arg in ('-h', '--help'):
                    if help_pos == -1:
                        help_pos = index
                index = index + 1
            if command_pos > -1 and help_pos > command_pos:
                argv = ['help', argv[command_pos]]
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
                        " either --os_token or env[OS_TOKEN]")

                if not self.options.os_url:
                    raise exc.CommandError(
                        "You must provide a service URL via"
                        " either --os_url or env[OS_URL]")

            else:
                # Validate password flow auth
                if not self.options.os_username:
                    raise exc.CommandError(
                        "You must provide a username via"
                        " either --os_username or env[OS_USERNAME]")

                if not self.options.os_password:
                    raise exc.CommandError(
                        "You must provide a password via"
                        " either --os_password or env[OS_PASSWORD]")

                if not (self.options.os_tenant_name):
                    raise exc.CommandError(
                        "You must provide a tenant_name via"
                        " either --os_tenant_name or via env[OS_TENANT_NAME]")

                if not self.options.os_auth_url:
                    raise exc.CommandError(
                        "You must provide an auth url via"
                        " either --os_auth_url or via env[OS_AUTH_URL]")
        else:   # not keystone
            if not self.options.os_url:
                raise exc.CommandError(
                    "You must provide a service URL via"
                    " either --os_url or env[OS_URL]")

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


def itertools_compressdef(data, selectors):
    # patch 2.6 compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
    return (d for d, s in itertools.izip(data, selectors) if s)


def main(argv=sys.argv[1:]):
    try:
        if not getattr(itertools, 'compress', None):
            setattr(itertools, 'compress', itertools_compressdef)
        return QuantumShell(QUANTUM_API_VERSION).run(argv)
    except exc.QuantumClientException:
        return 1
    except Exception as e:
        print e
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
