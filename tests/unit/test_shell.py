# Copyright (C) 2013 Yahoo! Inc.
# All Rights Reserved.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import cStringIO
import os
import re
import sys

import fixtures
import mox
import testtools
from testtools import matchers

from neutronclient.common import exceptions
from neutronclient import shell as openstack_shell


DEFAULT_USERNAME = 'username'
DEFAULT_PASSWORD = 'password'
DEFAULT_TENANT_ID = 'tenant_id'
DEFAULT_TENANT_NAME = 'tenant_name'
DEFAULT_AUTH_URL = 'http://127.0.0.1:5000/v2.0/'
DEFAULT_TOKEN = '3bcc3d3a03f44e3d8377f9247b0ad155'
DEFAULT_URL = 'http://quantum.example.org:9696/'


class NoExitArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise exceptions.CommandError(message)


class ShellTest(testtools.TestCase):

    FAKE_ENV = {
        'OS_USERNAME': DEFAULT_USERNAME,
        'OS_PASSWORD': DEFAULT_PASSWORD,
        'OS_TENANT_ID': DEFAULT_TENANT_ID,
        'OS_TENANT_NAME': DEFAULT_TENANT_NAME,
        'OS_AUTH_URL': DEFAULT_AUTH_URL}

    def _tolerant_shell(self, cmd):
        t_shell = openstack_shell.NeutronShell('2.0')
        t_shell.run(cmd.split())

    # Patch os.environ to avoid required auth info.
    def setUp(self):
        super(ShellTest, self).setUp()
        self.mox = mox.Mox()
        for var in self.FAKE_ENV:
            self.useFixture(
                fixtures.EnvironmentVariable(
                    var, self.FAKE_ENV[var]))

        # Make a fake shell object, a helping wrapper to call it, and a quick
        # way of asserting that certain API calls were made.
        global shell, _shell, assert_called, assert_called_anytime
        _shell = openstack_shell.NeutronShell('2.0')
        shell = lambda cmd: _shell.run(cmd.split())

    def shell(self, argstr):
        orig = sys.stdout
        clean_env = {}
        _old_env, os.environ = os.environ, clean_env.copy()
        try:
            sys.stdout = cStringIO.StringIO()
            _shell = openstack_shell.NeutronShell('2.0')
            _shell.run(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
            os.environ = _old_env
        return out

    def test_run_unknown_command(self):
        openstack_shell.NeutronShell('2.0').run('fake')

    def test_help(self):
        required = 'usage:'
        help_text = self.shell('help')
        self.assertThat(
            help_text,
            matchers.MatchesRegex(required))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: .* quota-list']
        stdout = self.shell('help quota-list')
        for r in required:
            self.assertThat(
                stdout,
                matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_command(self):
        required = 'usage:'
        help_text = self.shell('help network-create')
        self.assertThat(
            help_text,
            matchers.MatchesRegex(required))

    def test_unknown_auth_strategy(self):
        self.shell('--os-auth-strategy fake quota-list')

    def test_auth(self):
        self.shell(' --os-username test'
                   ' --os-password test'
                   ' --os-tenant-name test'
                   ' --os-auth-url http://127.0.0.1:5000/'
                   ' --os-auth-strategy keystone quota-list')

    def test_build_option_parser(self):
        neutron_shell = openstack_shell.NeutronShell('2.0')
        result = neutron_shell.build_option_parser('descr', '2.0')
        self.assertEqual(True, isinstance(result, argparse.ArgumentParser))

    def test_main_with_unicode(self):
        self.mox.StubOutClassWithMocks(openstack_shell, 'NeutronShell')
        qshell_mock = openstack_shell.NeutronShell('2.0')
        #self.mox.StubOutWithMock(qshell_mock, 'run')
        unicode_text = u'\u7f51\u7edc'
        argv = ['net-list', unicode_text, unicode_text.encode('utf-8')]
        qshell_mock.run([u'net-list', unicode_text,
                         unicode_text]).AndReturn(0)
        self.mox.ReplayAll()
        ret = openstack_shell.main(argv=argv)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        self.assertEqual(ret, 0)

    def test_endpoint_option(self):
        shell = openstack_shell.NeutronShell('2.0')
        parser = shell.build_option_parser('descr', '2.0')

        # Neither $OS_ENDPOINT_TYPE nor --endpoint-type
        namespace = parser.parse_args([])
        self.assertEqual('publicURL', namespace.endpoint_type)

        # --endpoint-type but not $OS_ENDPOINT_TYPE
        namespace = parser.parse_args(['--endpoint-type=admin'])
        self.assertEqual('admin', namespace.endpoint_type)

    def test_endpoint_environment_variable(self):
        fixture = fixtures.EnvironmentVariable("OS_ENDPOINT_TYPE",
                                               "public")
        self.useFixture(fixture)

        shell = openstack_shell.NeutronShell('2.0')
        parser = shell.build_option_parser('descr', '2.0')

        # $OS_ENDPOINT_TYPE but not --endpoint-type
        namespace = parser.parse_args([])
        self.assertEqual("public", namespace.endpoint_type)

        # --endpoint-type and $OS_ENDPOINT_TYPE
        namespace = parser.parse_args(['--endpoint-type=admin'])
        self.assertEqual('admin', namespace.endpoint_type)
