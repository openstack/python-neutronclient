# Copyright (c) 2016 IBM
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from neutronclient._i18n import _


def add_dns_argument_create(parser, resource, attribute):
    # Add dns_name and dns_domain support to network, port and floatingip
    # create
    argument = '--dns-%s' % attribute
    parser.add_argument(
        argument,
        help=_('Assign DNS %(attribute)s to the %(resource)s '
               '(requires DNS integration '
               'extension)') % {'attribute': attribute, 'resource': resource})


def args2body_dns_create(parsed_args, resource, attribute):
    # Add dns_name and dns_domain support to network, port and floatingip
    # create
    destination = 'dns_%s' % attribute
    argument = getattr(parsed_args, destination)
    if argument:
        resource[destination] = argument


def add_dns_argument_update(parser, resource, attribute):
    # Add dns_name and dns_domain support to network, port and floatingip
    # update
    argument = '--dns-%s' % attribute
    no_argument = '--no-dns-%s' % attribute
    dns_args = parser.add_mutually_exclusive_group()
    dns_args.add_argument(
        argument,
        help=_('Assign DNS %(attribute)s to the %(resource)s '
               '(requires DNS integration '
               'extension.)') % {'attribute': attribute, 'resource': resource})
    dns_args.add_argument(
        no_argument, action='store_true',
        help=_('Unassign DNS %(attribute)s from the %(resource)s '
               '(requires DNS integration '
               'extension.)') % {'attribute': attribute, 'resource': resource})


def args2body_dns_update(parsed_args, resource, attribute):
    # Add dns_name and dns_domain support to network, port and floatingip
    # update
    destination = 'dns_%s' % attribute
    no_destination = 'no_dns_%s' % attribute
    argument = getattr(parsed_args, destination)
    no_argument = getattr(parsed_args, no_destination)
    if argument:
        resource[destination] = argument
    if no_argument:
        resource[destination] = ""
