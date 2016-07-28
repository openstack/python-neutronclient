# Copyright 2016 NEC Corporation
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

"""This module should contain OSC plugin generic methods.

Methods in this module are candidates adopted to osc-lib.

Stuffs specific to neutronclient OSC plugin should not be added
to this module. They should go to neutronclient.osc.v2.utils.
"""

import operator

from keystoneclient import exceptions as identity_exc
from keystoneclient.v3 import domains
from keystoneclient.v3 import projects
from osc_lib import utils

from neutronclient._i18n import _


LIST_BOTH = 'both'
LIST_SHORT_ONLY = 'short_only'
LIST_LONG_ONLY = 'long_only'


def get_column_definitions(attr_map, long_listing):
    """Return table headers and column names for a listing table.

    :param attr_map: a list of table entry definitions.
      Each entry should be a tuple consisting of
      (API attribute name, header name, listing mode). For example:
      (('id', 'ID', LIST_BOTH),
       ('name', 'Name', LIST_BOTH),
       ('tenant_id', 'Project', LIST_LONG_ONLY))
      The third field of each tuple must be one of LIST_BOTH,
      LIST_LONG_ONLY (a corresponding column is shown only in a long mode), or
      LIST_SHORT_ONLY (a corresponding column is shown only in a short mode).
    :param long_listing: A boolean value which indicates a long listing
      or not. In most cases, parsed_args.long is passed to this argument.
    :return: A tuple of a list of table headers and a list of column names.
    """

    if long_listing:
        headers = [hdr for col, hdr, listing_mode in attr_map
                   if listing_mode in (LIST_BOTH, LIST_LONG_ONLY)]
        columns = [col for col, hdr, listing_mode in attr_map
                   if listing_mode in (LIST_BOTH, LIST_LONG_ONLY)]
    else:
        headers = [hdr for col, hdr, listing_mode in attr_map if listing_mode
                   if listing_mode in (LIST_BOTH, LIST_SHORT_ONLY)]
        columns = [col for col, hdr, listing_mode in attr_map if listing_mode
                   if listing_mode in (LIST_BOTH, LIST_SHORT_ONLY)]

    return headers, columns


def get_columns(item, attr_map=None):
    """Return pair of resource attributes and corresponding display names.

    Assume the following item and attr_map are passed.
    item: {'id': 'myid', 'name': 'myname',
           'foo': 'bar', 'tenant_id': 'mytenan'}
    attr_map:
      (('id', 'ID', LIST_BOTH),
       ('name', 'Name', LIST_BOTH),
       ('tenant_id', 'Project', LIST_LONG_ONLY))

    This method returns:

       (('id', 'name', 'tenant_id', 'foo'),  # attributes
        ('ID', 'Name', 'Project', 'foo')     # display names

    Both tuples of attributes and display names are sorted by display names
    in the alphabetical order.
    Attributes not found in a given attr_map are kept as-is.

    :param item: a dictionary which represents a resource.
      Keys of the dictionary are expected to be attributes of the resource.
      Values are not referred to by this method.
    :param attr_map: a list of mapping from attribute to display name.
      The same format is used as for get_column_definitions attr_map.
    :return: A pair of tuple of attributes and tuple of display names.
    """
    attr_map = attr_map or tuple([])
    _attr_map_dict = dict((col, hdr) for col, hdr, listing_mode in attr_map)

    columns = [(column, _attr_map_dict.get(column, column))
               for column in item.keys()]
    columns = sorted(columns, key=operator.itemgetter(1))
    return (tuple(col[0] for col in columns),
            tuple(col[1] for col in columns))


# TODO(amotoki): Use osc-lib version once osc-lib provides this.
def add_project_owner_option_to_parser(parser):
    """Register project and project domain options.

    :param parser: argparse.Argument parser object.

    """
    parser.add_argument(
        '--project',
        metavar='<project>',
        help=_("Owner's project (name or ID)")
    )
    # Borrowed from openstackclient.identity.common
    # as it is not exposed officially.
    parser.add_argument(
        '--project-domain',
        metavar='<project-domain>',
        help=_('Domain the project belongs to (name or ID). '
               'This can be used in case collisions between project names '
               'exist.'),
    )


# The following methods are borrowed from openstackclient.identity.common
# as it is not exposed officially.
# TODO(amotoki): Use osc-lib version once osc-lib provides this.


def find_domain(identity_client, name_or_id):
    return _find_identity_resource(identity_client.domains, name_or_id,
                                   domains.Domain)


def find_project(identity_client, name_or_id, domain_name_or_id=None):
    domain_id = _get_domain_id_if_requested(identity_client, domain_name_or_id)
    if not domain_id:
        return _find_identity_resource(identity_client.projects, name_or_id,
                                       projects.Project)
    else:
        return _find_identity_resource(identity_client.projects, name_or_id,
                                       projects.Project, domain_id=domain_id)


def _get_domain_id_if_requested(identity_client, domain_name_or_id):
    if not domain_name_or_id:
        return None
    domain = find_domain(identity_client, domain_name_or_id)
    return domain.id


def _find_identity_resource(identity_client_manager, name_or_id,
                            resource_type, **kwargs):
    """Find a specific identity resource.

    Using keystoneclient's manager, attempt to find a specific resource by its
    name or ID. If Forbidden to find the resource (a common case if the user
    does not have permission), then return the resource by creating a local
    instance of keystoneclient's Resource.

    The parameter identity_client_manager is a keystoneclient manager,
    for example: keystoneclient.v3.users or keystoneclient.v3.projects.

    The parameter resource_type is a keystoneclient resource, for example:
    keystoneclient.v3.users.User or keystoneclient.v3.projects.Project.

    :param identity_client_manager: the manager that contains the resource
    :type identity_client_manager: `keystoneclient.base.CrudManager`
    :param name_or_id: the resources's name or ID
    :type name_or_id: string
    :param resource_type: class that represents the resource type
    :type resource_type: `keystoneclient.base.Resource`

    :returns: the resource in question
    :rtype: `keystoneclient.base.Resource`

    """

    try:
        identity_resource = utils.find_resource(identity_client_manager,
                                                name_or_id, **kwargs)
        if identity_resource is not None:
            return identity_resource
    except identity_exc.Forbidden:
        pass

    return resource_type(None, {'id': name_or_id, 'name': name_or_id})


# The above are borrowed from openstackclient.identity.common.
# DO NOT ADD original methods in neutronclient repo to the above area.
