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

==================================
python-neutronclient documentation
==================================

This is a client for OpenStack Networking API. It provides
:doc:`Python API bindings <reference/index>` (the neutronclient module) and
:doc:`command-line interface (CLI) <cli/index>`.

There are two CLIs which support the Networking API:
:doc:`neutron CLI <cli/neutron>` and
`OpenStack Client (OSC) <https://docs.openstack.org/python-openstackclient/latest/>`__.
OpenStack Client provides the basic network commands and
python-neutronclient provides extensions (aka OSC plugins)
for advanced networking services.

User Documentation
------------------

.. toctree::
   :maxdepth: 2

   cli/index
   reference/index

Contributor Guide
-----------------

In the :doc:`Contributor Guide <contributor/index>`, you will find
information on neutronclient's lower level programming details or APIs
as well as the transition to OpenStack client.

.. toctree::
   :maxdepth: 2

   contributor/index

.. note::

   neutron CLI has been deprecated from Ocata release.
   We do not add, change and drop any existing commands any more.
   We only accept changes on OSC plugin, neutronclient python bindings
   and bug fixes on the deprecated CLI (``neutron`` command).

History
-------

Release notes is available at
http://docs.openstack.org/releasenotes/python-neutronclient/.
