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

Python bindings to the OpenStack Networking API
===============================================

This is a client for OpenStack Networking API. There is a :doc:`Python API
<usage/library>` (the neutronclient module), and a :doc:`command-line script
<usage/cli>` (installed as **neutron**). Each implements the entire OpenStack
Networking API.

Using neutronclient
-------------------

.. toctree::
   :maxdepth: 2

   usage/cli
   usage/library

Developer Guide
---------------

In the Developer Guide, you will find information on Neutron’s client
lower level programming details or APIs as well as the transition to
OpenStack client.

.. toctree::
   :maxdepth: 2

   devref/client_command_extensions
   devref/cli_option_guideline
   devref/transition_to_osc

History
-------

Release notes is available at
http://docs.openstack.org/releasenotes/python-neutronclient/.
