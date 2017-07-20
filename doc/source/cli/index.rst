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

=========
Using CLI
=========

There are two CLIs which support the Networking API:
`OpenStackClient (OSC)
<https://docs.openstack.org/python-openstackclient/latest/>`__
and :doc:`neutron CLI <neutron>` (deprecated).

OpenStackClient
---------------

OpenStackClient provides
`the basic network commands <https://docs.openstack.org/python-openstackclient/latest/cli/command-list.html>`__
and python-neutronclient provides :doc:`extensions <osc_plugins>`
(aka OSC plugins) for advanced networking services.

.. toctree::
   :maxdepth: 1

   Basic network commands <https://docs.openstack.org/python-openstackclient/latest/cli/command-list.html>
   Network commands for advanced networking services <osc_plugins>
   Mapping Guide from neutron CLI <https://docs.openstack.org/python-openstackclient/latest/cli/decoder.html#neutron-cli>

neutron CLI
-----------

.. warning::

   neutron CLI is now deprecated and will be removed in the future.
   Use openstack CLI instead. See `openstack CLI command list
   <https://docs.openstack.org/python-openstackclient/latest/cli/command-list.html>`__
   and :doc:`its extensions for advanced networking services <osc_plugins>`.
   The command mapping from neutron CLI to openstack CLI is available
   `here <https://docs.openstack.org/python-openstackclient/latest/cli/decoder.html#neutron-cli>`__.

.. toctree::
   :maxdepth: 2

   neutron CLI guide <neutron>
   neutron CLI reference <neutron-reference>
