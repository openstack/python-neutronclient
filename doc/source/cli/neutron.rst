..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.


      Convention for heading levels in Neutron devref:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

Using neutron CLI
=================

The **neutron** shell utility interacts with OpenStack Networking API from the
command-line. It supports the entire features of OpenStack Networking API.

.. warning::

   neutron CLI is now deprecated and will be removed in the future.
   Use openstack CLI instead. See `openstack CLI command list
   <https://docs.openstack.org/python-openstackclient/latest/cli/command-list.html>`__
   and :doc:`its extensions for advanced networking services <osc_plugins>`.
   The command mapping from neutron CLI to openstack CLI is available
   `here <https://docs.openstack.org/python-openstackclient/latest/cli/decoder.html#neutron-cli>`__.

Basic Usage
-----------

In order to use the CLI, you must provide your OpenStack username, password,
project, domain information for both user and project, and auth endpoint. Use
the corresponding configuration options (``--os-username``, ``--os-password``,
``--os-project-name``, ``--os-user-domain-id``, ``os-project-domain-id``, and
``--os-auth-url``), but it is easier to set them in environment variables.

.. code-block:: shell

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_PROJECT_NAME=project
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_DOMAIN_ID=default
    export OS_AUTH_URL=http://auth.example.com:5000/v3

If you are using Identity v2.0 API (DEPRECATED), you don't need to pass domain
information.

.. code-block:: shell

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_TENANT_NAME=tenant
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0

Once you've configured your authentication parameters, you can run **neutron**
commands.  All commands take the form of:

.. code-block:: none

    neutron <command> [arguments...]

Run **neutron help** to get a full list of all possible commands, and run
**neutron help <command>** to get detailed help for that command.

Using with os-client-config
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`os-client-config <https://docs.openstack.org/os-client-config/latest/>`_
provides more convenient way to manage a collection of client configurations
and you can easily switch multiple OpenStack-based configurations.

To use os-client-config, you first need to prepare
``~/.config/openstack/clouds.yaml`` like the following.

.. code-block:: yaml

    clouds:
      devstack:
        auth:
          auth_url: http://auth.example.com:5000
          password: your-secret
          project_domain_id: default
          project_name: demo
          user_domain_id: default
          username: demo
        identity_api_version: '3'
        region_name: RegionOne
      devstack-admin:
        auth:
          auth_url: http://auth.example.com:35357
          password: another-secret
          project_domain_id: default
          project_name: admin
          user_domain_id: default
          username: admin
        identity_api_version: '3'
        region_name: RegionOne

Then, you need to specify a configuration name defined in the above clouds.yaml.

.. code-block:: shell

    export OS_CLOUD=devstack

For more detail information, see the
`os-client-config <https://docs.openstack.org/os-client-config/latest/>`_
documentation.

Using with keystone token
~~~~~~~~~~~~~~~~~~~~~~~~~

The command-line tool will attempt to re-authenticate using your provided
credentials for every request. You can override this behavior by manually
supplying an auth token using ``--os-url`` and ``--os-auth-token``. You can
alternatively set these environment variables.

.. code-block:: shell

    export OS_URL=http://neutron.example.org:9696/
    export OS_TOKEN=3bcc3d3a03f44e3d8377f9247b0ad155

Using noauth mode
~~~~~~~~~~~~~~~~~

If neutron server does not require authentication, besides these two arguments
or environment variables (We can use any value as token.), we need manually
supply ``--os-auth-strategy`` or set the environment variable.

.. code-block:: shell

    export OS_AUTH_STRATEGY=noauth

Display options
---------------

Filtering
~~~~~~~~~

Neutron API supports filtering in the listing operation.
**neutron** CLI supports this feature too.

To specify a filter in ``*-list`` command, you need to pass a pair of an
attribute name and an expected value with the format of ``--<attribute> <value>``.
The example below retrieves ports owned by compute instances.

.. code-block:: console

    $ neutron port-list --device_owner network:dhcp
    +--------------------------------------+------+-------------------+-------------------------------------------------------------------------------------------------------------+
    | id                                   | name | mac_address       | fixed_ips                                                                                                   |
    +--------------------------------------+------+-------------------+-------------------------------------------------------------------------------------------------------------+
    | 8953d683-29ad-4be3-b73f-060727c7849b |      | fa:16:3e:4b:9e:0a | {"subnet_id": "6b832dfe-f271-443c-abad-629961414a73", "ip_address": "10.0.0.2"}                             |
    |                                      |      |                   | {"subnet_id": "cdcc616b-0cff-482f-96f5-06fc63d21247", "ip_address": "fd12:877c:1d66:0:f816:3eff:fe4b:9e0a"} |
    +--------------------------------------+------+-------------------+-------------------------------------------------------------------------------------------------------------+

You can also specify multiple filters.
The example below retrieves security group rules applied to IPv4 traffic
which belongs to a security group bfa493f9-2b03-46d2-8399-b9b038a53bc1.

.. code-block:: console

    $ neutron security-group-rule-list --security-group-id bfa493f9-2b03-46d2-8399-b9b038a53bc1 --ethertype IPv4
    +--------------------------------------+----------------+-----------+-----------+---------------+-----------------+
    | id                                   | security_group | direction | ethertype | protocol/port | remote          |
    +--------------------------------------+----------------+-----------+-----------+---------------+-----------------+
    | 65489805-0400-4bce-9bd9-16a81952263c | default        | egress    | IPv4      | any           | any             |
    | 9429f336-4947-4643-bbd9-24528cc65648 | default        | ingress   | IPv4      | any           | default (group) |
    +--------------------------------------+----------------+-----------+-----------+---------------+-----------------+

.. note::

   Looking up UUID from name is not supported when specifying a filter.
   You need to use UUID to specify a specific resource.

.. note::

   Filtering for dictionary or list attributes is not supported.

Changing displayed columns
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want displayed columns in a list operation, ``-c`` option can be used.
``-c`` can be specified multiple times and the column order will be same as
the order of ``-c`` options.

.. code-block:: console

    $ neutron port-list -c id -c device_owner -c fixed_ips
    +--------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------+
    | id                                   | device_owner             | fixed_ips                                                                                                   |
    +--------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------+
    | 41ca1b9b-4bbd-4aa8-bcaa-31d3d5704205 | network:router_interface | {"subnet_id": "6b832dfe-f271-443c-abad-629961414a73", "ip_address": "10.0.0.1"}                             |
    | 8953d683-29ad-4be3-b73f-060727c7849b | network:dhcp             | {"subnet_id": "6b832dfe-f271-443c-abad-629961414a73", "ip_address": "10.0.0.2"}                             |
    |                                      |                          | {"subnet_id": "cdcc616b-0cff-482f-96f5-06fc63d21247", "ip_address": "fd12:877c:1d66:0:f816:3eff:fe4b:9e0a"} |
    | a9da29f8-4504-4526-a5ce-cd3624fbd173 | neutron:LOADBALANCER     | {"subnet_id": "6b832dfe-f271-443c-abad-629961414a73", "ip_address": "10.0.0.3"}                             |
    |                                      |                          | {"subnet_id": "cdcc616b-0cff-482f-96f5-06fc63d21247", "ip_address": "fd12:877c:1d66:0:f816:3eff:feb1:ab71"} |
    | d6a1ff96-0a99-416f-a4d6-65d9614cf64e | compute:nova             | {"subnet_id": "6b832dfe-f271-443c-abad-629961414a73", "ip_address": "10.0.0.4"}                             |
    |                                      |                          | {"subnet_id": "cdcc616b-0cff-482f-96f5-06fc63d21247", "ip_address": "fd12:877c:1d66:0:f816:3eff:fe2c:348e"} |
    | f4789225-26d0-409f-8047-82d2c7a87a95 | network:router_interface | {"subnet_id": "cdcc616b-0cff-482f-96f5-06fc63d21247", "ip_address": "fd12:877c:1d66::1"}                    |
    +--------------------------------------+--------------------------+-------------------------------------------------------------------------------------------------------------+

.. _cli_extra_arguments:

Extra arguments for create/update operation
-------------------------------------------

**neutron** CLI has a mechanism called the *extra arguments* for ``*-create``
and ``*-update`` commands. It allows users to specify a set of *unknown
options* which are not defined as options and not shown in the help text.
**Unknown options MUST be placed at the end of the command line.**
*unknown options* will be directly passed to the API layer.  By this mechanism,
you can pass an attribute which is not defined in the upstream **neutron**
CLI. For example, when you are developing a new feature which add a new
attribute to an existing resource, it is useful because we can test your
feature without changing the existing neutron CLI.

For example, if you run the following command::

    neutron resource-update <ID> --key1 value1 --key2 value2

where ``resource`` is some resource name and ``--key1`` and ``--key2`` are
unknown options, then the following JSON will be sent to the neutron API::

    PUT /v2.0/resources/<ID>

    {
        "resource": {
            "key2": "value2",
            "key1": "value1"
        }
    }

Key interpretation
~~~~~~~~~~~~~~~~~~

This means an option name (``--key1`` in this case) must be one of valid
resources of a corresponding resource. An option name ``--foo_bar`` is
recognized as an attribute name ``foo_bar``. ``--foo-bar`` is also interpreted
as an attribute name ``foo_bar``.

Value interpretation
~~~~~~~~~~~~~~~~~~~~

By default, if the number of values is 1, the option value is interpreted as a
string and is passed to the API layer as specified in a command-line.

If the number of values is greater than 1, the option value is interpreted as a
list and the result in the API layer will be same as when specifying a list as
described below.

    neutron resource-update <ID> --key1 val1 val2 val3 --key2 val4

In the above example, a value of ``key1`` is interpreted as
``["val1", "val2", "val3"]`` and a value of ``key2`` is interpreted
as ``val4``.

The extra argument mechanism supports more complex value like a list or a dict.

Specify a list value
++++++++++++++++++++

A command-line::

    neutron resource-update <ID> --key list=true val1 val2 val3

will send the following in the API layer::

    {
        "key": [
            "val1",
            "val2",
            "val3"
        ]
    }

.. note::

   If you want to specify a list value, it is recommended to specify
   ``list=true``. When ``list=true`` is specified, specified values are
   interpreted as a list even regardless of the number of values.

   If ``list=true`` is not specified, specified values are interpreted
   depends on the number of values how. If the number of values is more than 2,
   the specified values are interpreted as a list. If 1, the value
   is interpreted as a string.

Specify a dict value
++++++++++++++++++++

A command-line::

    neutron resource-update <ID> --key type=dict key1=val1,key2=val2,key3=val3

will send the following in the API layer::

    {
        "key": {
            "key1": "val1",
            "key2": "val2",
            "key3": "val3"
        }
    }

.. note::

   ``type=bool True/False`` and ``type=int 10`` are also supported.

Specify a list of dicts
+++++++++++++++++++++++

A command-line::

    neutron resource-update <ID> --key type=dict list=true key1=val1 key2=val2 key3=val3

will send the following in the API layer::

    {
        "key": [
            {"key1": "val1"},
            {"key2": "val2"},
            {"key3": "val3"}
        ]
    }

Passing None as a value
~~~~~~~~~~~~~~~~~~~~~~~

There is a case where we would like to pass ``None`` (``null`` in JSON)
in the API layer. To do this::

    neutron resource-update <ID> --key action=clear

The following body will be in the API layer::

    {"key": null}

.. note::

   If ``action=clear`` is specified, ``list=true`` or ``type=dict`` is ignored.
   It means when ``action=clear`` is specified ``None`` is always sent.

Debugging
---------

Display API-level communication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``-v`` (or ``--verbose``, ``--debug``) option displays a detail interaction
with your neutron server. It is useful to debug what happens in the API level.

Here is an sample output of ``net-show`` command.

The first line show what parameters are recognized by neutronclient.
It is sometimes useful to check if command-line parameters you specify are recognized properly.

.. code-block:: console

    $ neutron -v net-show mynetwork
    DEBUG: neutronclient.neutron.v2_0.network.ShowNetwork get_data(Namespace(columns=[], fields=[], formatter='table', id=u'mynetwork', max_width=0, noindent=False, prefix='', request_format='json', show_details=False, variables=[]))

Next, neutronclient sends an authentication request to keystone to get a token
which is used in further operations.

.. code-block:: console

    DEBUG: keystoneauth.session REQ: curl -g -i -X GET http://172.16.18.47:5000 -H "Accept: application/json" -H "User-Agent: keystoneauth1"
    DEBUG: keystoneauth.session RESP: [300] Content-Length: 593 Vary: X-Auth-Token Keep-Alive: timeout=5, max=100 Server: Apache/2.4.7 (Ubuntu) Connection: Keep-Alive Date: Fri, 27 Nov 2015 20:10:54 GMT Content-Type: application/json
    RESP BODY: {"versions": {"values": [{"status": "stable", "updated": "2015-03-30T00:00:00Z", "media-types": [{"base": "application/json", "type": "application/vnd.openstack.identity-v3+json"}], "id": "v3.4", "links": [{"href": "http://172.16.18.47:5000/v3/", "rel": "self"}]}, {"status": "stable", "updated": "2014-04-17T00:00:00Z", "media-types": [{"base": "application/json", "type": "application/vnd.openstack.identity-v2.0+json"}], "id": "v2.0", "links": [{"href": "http://172.16.18.47:5000/v2.0/", "rel": "self"}, {"href": "http://docs.openstack.org/", "type": "text/html", "rel": "describedby"}]}]}}

    DEBUG: keystoneauth.identity.v3.base Making authentication request to http://172.16.18.47:5000/v3/auth/tokens

Neutronclient looks up a network ID corresponding to a given network name.

.. code-block:: console

    DEBUG: keystoneauth.session REQ: curl -g -i -X GET http://172.16.18.47:9696/v2.0/networks.json?fields=id&name=mynetwork -H "User-Agent: python-neutronclient" -H "Accept: application/json" -H "X-Auth-Token: {SHA1}39300e7398d53a02afd183f13cb6afaef95ec4e5"
    DEBUG: keystoneauth.session RESP: [200] Date: Fri, 27 Nov 2015 20:10:55 GMT Connection: keep-alive Content-Type: application/json; charset=UTF-8 Content-Length: 62 X-Openstack-Request-Id: req-ccebf6e4-4f52-4874-a1ab-5499abcba378
    RESP BODY: {"networks": [{"id": "3698d3c7-d581-443e-bf86-53c4e3a738f7"}]}

Finally, neutronclient retrieves a detail of a given network using the resolved ID.

.. code-block:: console

    DEBUG: keystoneauth.session REQ: curl -g -i -X GET http://172.16.18.47:9696/v2.0/networks/3698d3c7-d581-443e-bf86-53c4e3a738f7.json -H "User-Agent: python-neutronclient" -H "Accept: application/json" -H "X-Auth-Token: {SHA1}39300e7398d53a02afd183f13cb6afaef95ec4e5"
    DEBUG: keystoneauth.session RESP: [200] Date: Fri, 27 Nov 2015 20:10:55 GMT Connection: keep-alive Content-Type: application/json; charset=UTF-8 Content-Length: 272 X-Openstack-Request-Id: req-261add00-d6d3-4ea7-becc-105b60ac7369
    RESP BODY: {"network": {"status": "ACTIVE", "subnets": [], "name": "mynetwork", "admin_state_up": true, "tenant_id": "8f0ebf767043483a987736c8c684178d", "mtu": 0, "router:external": false, "shared": false, "port_security_enabled": true, "id": "3698d3c7-d581-443e-bf86-53c4e3a738f7"}}

    +-----------------------+--------------------------------------+
    | Field                 | Value                                |
    +-----------------------+--------------------------------------+
    | admin_state_up        | True                                 |
    | id                    | 3698d3c7-d581-443e-bf86-53c4e3a738f7 |
    | mtu                   | 0                                    |
    | name                  | mynetwork                            |
    | port_security_enabled | True                                 |
    | router:external       | False                                |
    | shared                | False                                |
    | status                | ACTIVE                               |
    | subnets               |                                      |
    | tenant_id             | 8f0ebf767043483a987736c8c684178d     |
    +-----------------------+--------------------------------------+
