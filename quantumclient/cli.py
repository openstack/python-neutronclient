# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nicira Networks, Inc.
# Copyright 2012 Citrix Systems
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
# @author: Somik Behera, Nicira Networks, Inc.
# @author: Brad Hall, Nicira Networks, Inc.
# @author: Salvatore Orlando, Citrix

import logging
import logging.handlers
from optparse import OptionParser
import os
import sys

from quantumclient import cli_lib
from quantumclient import Client
from quantumclient import ClientV11
from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient import net_filters_v11
from quantumclient import port_filters_v11

# Configure logger for client - cli logger is a child of it
# NOTE(salvatore-orlando): logger name does not map to package
# this is deliberate. Simplifies logger configuration
logging.basicConfig()
LOG = logging.getLogger('quantumclient')


DEFAULT_QUANTUM_VERSION = '1.1'
FORMAT = 'json'
commands_v10 = {
    "list_nets": {
        "func": cli_lib.list_nets,
        "args": ["tenant-id"], },
    "list_nets_detail": {
        "func": cli_lib.list_nets_detail,
        "args": ["tenant-id"], },
    "create_net": {
        "func": cli_lib.create_net,
        "args": ["tenant-id", "net-name"], },
    "delete_net": {
        "func": cli_lib.delete_net,
        "args": ["tenant-id", "net-id"], },
    "show_net": {
        "func": cli_lib.show_net,
        "args": ["tenant-id", "net-id"], },
    "show_net_detail": {
        "func": cli_lib.show_net_detail,
        "args": ["tenant-id", "net-id"], },
    "update_net": {
        "func": cli_lib.update_net,
        "args": ["tenant-id", "net-id", "new-name"], },
    "list_ports": {
        "func": cli_lib.list_ports,
        "args": ["tenant-id", "net-id"], },
    "list_ports_detail": {
        "func": cli_lib.list_ports_detail,
        "args": ["tenant-id", "net-id"], },
    "create_port": {
        "func": cli_lib.create_port,
        "args": ["tenant-id", "net-id"], },
    "delete_port": {
        "func": cli_lib.delete_port,
        "args": ["tenant-id", "net-id", "port-id"], },
    "update_port": {
        "func": cli_lib.update_port,
        "args": ["tenant-id", "net-id", "port-id", "params"], },
    "show_port": {
        "func": cli_lib.show_port,
        "args": ["tenant-id", "net-id", "port-id"], },
    "show_port_detail": {
        "func": cli_lib.show_port_detail,
        "args": ["tenant-id", "net-id", "port-id"], },
    "plug_iface": {
        "func": cli_lib.plug_iface,
        "args": ["tenant-id", "net-id", "port-id", "iface-id"], },
    "unplug_iface": {
        "func": cli_lib.unplug_iface,
        "args": ["tenant-id", "net-id", "port-id"], },
    "show_iface": {
        "func": cli_lib.show_iface,
        "args": ["tenant-id", "net-id", "port-id"], }, }

commands_v11 = commands_v10.copy()
commands_v11.update({
    "list_nets": {
        "func": cli_lib.list_nets_v11,
        "args": ["tenant-id"],
        "filters": net_filters_v11, },
    "list_nets_detail": {
        "func": cli_lib.list_nets_detail_v11,
        "args": ["tenant-id"],
        "filters": net_filters_v11, },
    "list_ports": {
        "func": cli_lib.list_ports_v11,
        "args": ["tenant-id", "net-id"],
        "filters": port_filters_v11, },
    "list_ports_detail": {
        "func": cli_lib.list_ports_detail_v11,
        "args": ["tenant-id", "net-id"],
        "filters": port_filters_v11, }, })
commands = {
    '1.0': commands_v10,
    '1.1': commands_v11, }
clients = {
    '1.0': Client,
    '1.1': ClientV11, }


def help(version):
    print "\nCommands:"
    cmds = commands[version]
    for k in cmds.keys():
        print "    %s %s %s" % (
            k,
            " ".join(["<%s>" % y for y in cmds[k]["args"]]),
            'filters' in cmds[k] and "[filterspec ...]" or "")


def print_usage(cmd, version):
    cmds = commands[version]
    print "Usage:\n    %s %s" % (
        cmd, " ".join(["<%s>" % y for y in cmds[cmd]["args"]]))


def build_args(cmd, cmdargs, arglist):
    arglist_len = len(arglist)
    cmdargs_len = len(cmdargs)
    if arglist_len < cmdargs_len:
        message = ("Not enough arguments for \"%s\" (expected: %d, got: %d)" %
                   (cmd, len(cmdargs), arglist_len))
        raise exceptions.QuantumCLIError(message=message)
    args = arglist[:cmdargs_len]
    return args


def build_filters(cmd, cmd_filters, filter_list, version):
    filters = {}
    # Each filter is expected to be in the <key>=<value> format
    for flt in filter_list:
        split_filter = flt.split("=")
        if len(split_filter) != 2:
            message = "Invalid filter argument detected (%s)" % flt
            raise exceptions.QuantumCLIError(message=message)
        filter_key, filter_value = split_filter
        # Ensure the filter is allowed
        if not filter_key in cmd_filters:
            message = "Invalid filter key (%s)" % filter_key
            raise exceptions.QuantumCLIError(message=message)
        filters[filter_key] = filter_value
    return filters


def build_cmd(cmd, cmd_args, cmd_filters, arglist, version):
    """
    Builds arguments and filters to be passed to the cli library routines

    :param cmd: Command to be executed
    :param cmd_args: List of arguments required by the command
    :param cmd_filters: List of filters allowed by the command
    :param arglist: Command line arguments (includes both arguments and
                    filter specifications)
    :param version: API version
    """
    arglist_len = len(arglist)
    try:
        # Parse arguments
        args = build_args(cmd, cmd_args, arglist)
        # Parse filters
        filters = None
        if cmd_filters:
            # Pop consumed arguments
            arglist = arglist[len(args):]
            filters = build_filters(cmd, cmd_filters, arglist, version)
    except exceptions.QuantumCLIError as cli_ex:
        LOG.error(cli_ex.message)
        print " Error in command line:%s" % cli_ex.message
        print_usage(cmd, version)
        return None, None
    filter_len = (filters is not None) and len(filters) or 0
    if len(arglist) - len(args) - filter_len > 0:
        message = ("Too many arguments for \"%s\" (expected: %d, got: %d)" %
                   (cmd, len(cmd_args), arglist_len))
        LOG.error(message)
        print "Error in command line: %s " % message
        print "Usage:\n    %s %s" % (
            cmd,
            " ".join(["<%s>" % y for y in commands[version][cmd]["args"]]))
        return None, None
    # Append version to arguments for cli functions
    args.append(version)
    return args, filters


def instantiate_client(host, port, ssl, tenant, token, version):
    client = clients[version](host,
                              port,
                              ssl,
                              tenant,
                              FORMAT,
                              auth_token=token,
                              version=version)
    return client


def main():
    usagestr = "Usage: %prog [OPTIONS] <command> [args]"
    parser = OptionParser(usage=usagestr)
    parser.add_option("-H", "--host", dest="host",
                      type="string", default="127.0.0.1",
                      help="ip address of api host")
    parser.add_option("-p", "--port", dest="port",
                      type="int", default=9696, help="api poort")
    parser.add_option("-s", "--ssl", dest="ssl",
                      action="store_true", default=False, help="use ssl")
    parser.add_option("--debug", dest="debug",
                      action="store_true", default=False,
                      help="print debugging output")
    parser.add_option("-f", "--logfile", dest="logfile",
                      type="string", default="syslog", help="log file path")
    parser.add_option("-t", "--token", dest="token",
                      type="string", default=None, help="authentication token")
    parser.add_option(
        '--version',
        default=utils.env('QUANTUM_VERSION', default=DEFAULT_QUANTUM_VERSION),
        help='Accepts 1.1 and 1.0, defaults to env[QUANTUM_VERSION].')
    options, args = parser.parse_args()

    if options.debug:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.WARN)

    if options.logfile == "syslog":
        LOG.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))
    else:
        LOG.addHandler(logging.handlers.WatchedFileHandler(options.logfile))
        # Set permissions on log file
        os.chmod(options.logfile, 0644)

    version = options.version
    if not version in commands:
        LOG.error("Unknown API version specified:%s", version)
        parser.print_help()
        sys.exit(1)

    if len(args) < 1:
        parser.print_help()
        help(version)
        sys.exit(1)

    cmd = args[0]
    if cmd not in commands[version].keys():
        LOG.error("Unknown command: %s" % cmd)
        help(version)
        sys.exit(1)

    # Build argument list for CLI command
    # The argument list will include the version number as well
    args, filters = build_cmd(cmd,
                              commands[version][cmd]["args"],
                              commands[version][cmd].get("filters", None),
                              args[1:],
                              options.version)
    if not args:
        sys.exit(1)
    LOG.info("Executing command \"%s\" with args: %s" % (cmd, args))

    client = instantiate_client(options.host,
                                options.port,
                                options.ssl,
                                args[0],
                                options.token,
                                options.version)
    # append filters to arguments
    # this will allow for using the same prototype for v10 and v11
    # TODO: Use **kwargs instead of *args (keyword is better than positional)
    if filters:
        args.append(filters)
    commands[version][cmd]["func"](client, *args)

    LOG.info("Command execution completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
