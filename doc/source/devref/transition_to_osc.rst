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

Transition to OpenStack Client
==============================

This document details the transition roadmap for moving the neutron client's
OpenStack Networking API support, both the Python library and the ``neutron``
command-line interface (CLI), to the
`OpenStack client (OSC) <https://github.com/openstack/python-openstackclient>`_
and the `OpenStack Python SDK <https://github.com/openstack/python-openstacksdk>`_.
This transition is being guided by the
`Deprecate individual CLIs in favour of OSC <https://review.openstack.org/#/c/243348/>`_
OpenStack spec. See the `Neutron RFE <https://bugs.launchpad.net/neutron/+bug/1521291>`_ and
`OSC neutron-client blueprint <https://blueprints.launchpad.net/python-openstackclient/+spec/neutron-client>`_
for the overall progress of this transition.

Overview
--------

This transition will result in the neutron client's ``neutron`` CLI being
deprecated and then eventually removed. The ``neutron`` CLI will be replaced
by OSC's networking support available via the ``openstack`` CLI. This is
similar to the deprecation and removal process for the
`keystone client's <https://github.com/openstack/python-keystoneclient>`_
``keystone`` CLI.

The neutron client's Python library won't be deprecated. It will be available
along side the networking support provided by the OpenStack Python SDK. However,
the OpenStack Python SDK will be used to implement OSC's networking support.

Users of the neutron client's command extensions will need to transition to the
`OSC plugin system <http://docs.openstack.org/developer/python-openstackclient/plugins.html>`_
before the ``neutron`` CLI is removed. Such users will maintain their OSC plugin
within their own project and will be responsible for deprecating and removing
their ``neutron`` CLI extension.

Transition Steps
----------------

1. **Done:** OSC adds OpenStack Python SDK as a dependency. See the following
   patch set: https://review.openstack.org/#/c/138745/

2. **Done:** OSC switches its networking support for the
   `network <http://docs.openstack.org/developer/python-openstackclient/command-objects/network.html>`_
   command object to use the OpenStack Python SDK instead of the neutron
   client's Python library. See the following patch set:
   https://review.openstack.org/#/c/253348/

3. **Done:** OSC removes its python-neutronclient dependency.
   See the following patch set: https://review.openstack.org/#/c/255545/

4. **In Progress:** OpenStack Python SDK releases version 1.0 to guarantee
   backwards compatibility of its networking support and OSC updates
   its dependencies to include OpenStack Python SDK version 1.0 or later.

5. **In Progress:** OSC switches its networking support for the
   `ip floating <http://docs.openstack.org/developer/python-openstackclient/command-objects/ip-floating.html>`_,
   `ip floating pool <http://docs.openstack.org/developer/python-openstackclient/command-objects/ip-floating-pool.html>`_,
   `ip fixed <http://docs.openstack.org/developer/python-openstackclient/command-objects/ip-fixed.html>`_,
   `security group <http://docs.openstack.org/developer/python-openstackclient/command-objects/security-group.html>`_, and
   `security group rule <http://docs.openstack.org/developer/python-openstackclient/command-objects/security-group-rule.html>`_
   command objects to use the OpenStack Python SDK instead of the nova
   client's Python library when neutron is enabled. When nova network
   is enabled, then the nova client's Python library will continue to
   be used. See the following OSC bugs:

   * `Floating IP CRUD <https://bugs.launchpad.net/python-openstackclient/+bug/1519502>`_

   * `Port CRUD <https://bugs.launchpad.net/python-openstackclient/+bug/1519909>`_

   * `Security Group CRUD <https://bugs.launchpad.net/python-openstackclient/+bug/1519511>`_

   * `Security Group Rule CRUD <https://bugs.launchpad.net/python-openstackclient/+bug/1519512>`_

6. **In Progress:** OSC enhances its networking support under the
   `neutron-client <https://blueprints.launchpad.net/python-openstackclient/+spec/neutron-client>`_
   OSC spec. At this point and when applicable, enhancements to the ``neutron``
   CLI must also be made to the ``openstack`` CLI and the OpenStack Python SDK.
   Enhancements to the networking support in the OpenStack Python SDK will be
   handled via bugs. Neutron stadium users of the neutron client's command
   extensions should start their transition to the OSC plugin system.
   See the developer guide section below for more information on this step.

7. **Not Started:** Deprecate the ``neutron`` CLI once the criteria below have
   been meet. Running the CLI after it has been deprecated will issue a warning
   messages such as the following:
   ``DeprecationWarning: The neutron CLI is deprecated in favor of python-openstackclient.``
   In addition, only security fixes will be made to the CLI after it has been
   deprecated.

   * The networking support provide by the ``openstack`` CLI is functionally
     equivalent to the ``neutron`` CLI and it contains sufficient functional
     and unit test coverage.

   * Neutron core and advanced services projects, Neutron documentation and
     `DevStack <http://docs.openstack.org/developer/devstack/>`_ use ``openstack``
     CLI instead of ``neutron`` CLI.

   * Most neutron stadium users of the neutron client's command extensions have
     transitioned to the OSC plugin system and use the ``openstack`` CLI instead
     of the ``neutron`` CLI.

8. **Not Started:** Remove the ``neutron`` CLI after two deprecation cycles.

Developer Guide
---------------
The ``neutron`` CLI version 3.1.1, without extensions, supports over 200
commands while the ``openstack`` CLI version 2.0.1 supports about 20
networking commands. Of the 20 commands, most do not have all of the options
or arguments of their ``neutron`` CLI equivalent. With this large functional
gap, one critical question for developers during this transition is "Which
CLI do I change?" The answer depends on the state of a command and the
state of the overall transition. Details are outlined in the table
below. Early stages of the transition will require dual maintenance.
Eventually, dual maintenance will be reduced to critical bug fixes only
with feature requests only being made to the ``openstack`` CLI.

+----------------------+------------------------+----------------------------------------------+
| neutron Command      | openstack Command      | CLI to Change                                |
+======================+========================+==============================================+
| Exists               | Doesn't Exist          | neutron                                      |
+----------------------+------------------------+----------------------------------------------+
| Exists               | In Progress            | neutron and update related OSC bug           |
+----------------------+------------------------+----------------------------------------------+
| Exists               | Exists                 | neutron and openstack                        |
+----------------------+------------------------+----------------------------------------------+
| Doesn't Exist        | Doesn't Exist          | neutron and openstack                        |
+----------------------+------------------------+----------------------------------------------+
| Doesn't Exist        | Exists                 | openstack                                    |
+----------------------+------------------------+----------------------------------------------+

When adding or updating an ``openstack`` networking command, changes may
first be required to the OpenStack Python SDK to support the underlying
networking resource object, properties and/or actions. Once the OpenStack
Python SDK changes are merged, the related OSC changes can be merged.
The OSC changes may require an update to the OSC openstacksdk version in the
`requirements.txt <https://github.com/openstack/python-openstackclient/blob/master/requirements.txt>`_
file.

Neutron stadium users of the neutron client's command extensions must adopt the
`OSC plugin system <http://docs.openstack.org/developer/python-openstackclient/plugins.html>`_
for this transition. Such users will maintain their OSC plugin within their
own project and should follow the guidance in the table above to determine
which CLI to change.

Developer References
--------------------

* See `OSC neutron-client blueprint <https://blueprints.launchpad.net/python-openstackclient/+spec/neutron-client>`_
  to determine if an ``openstack`` command is in progress. See the ``Related bugs`` list.
* See `OSC command list <http://docs.openstack.org/developer/python-openstackclient/command-list.html>`_
  to determine if an ``openstack`` command exists.
* See `OSC plugin command list <http://docs.openstack.org/developer/python-openstackclient/plugin-commands.html>`_
  to determine if an ``openstack`` plugin command exists.
* See `OSC command structure <http://docs.openstack.org/developer/python-openstackclient/commands.html>`_
  to determine the current ``openstack`` command objects, plugin objects and actions.
* See `OSC human interface guide <http://docs.openstack.org/developer/python-openstackclient/humaninterfaceguide.html>`_
  for guidance on creating new OSC command interfaces.
* See `OSC plugin <http://docs.openstack.org/developer/python-openstackclient/plugins.html>`_
  for information on the OSC plugin system to be used for ``neutron`` CLI extensions.
* Report an OSC bug: https://bugs.launchpad.net/python-openstackclient/+filebug
* Report an OpenStack Python SDK bug: https://bugs.launchpad.net/python-openstacksdk/+filebug
