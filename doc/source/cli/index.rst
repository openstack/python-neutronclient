:orphan:

.. This page is to provide the top page for the CLI reference.
   On the other hand, it looks better that the top level document has
   direct links to individual pages for better navigation.
   From that reason, :orphan: is needed to silence sphinx warning.

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

=============
CLI reference
=============

There are two CLIs which support the Networking API:
:doc:`neutron CLI <neutron>` and
`OpenStack Client (OSC) <https://docs.openstack.org/developer/python-openstackclient/>`__.
OpenStack Client provides the basic network commands and
python-neutronclient provides :doc:`extensions <osc_plugins>` (aka OSC plugins)
for advanced networking services.

.. toctree::
   :maxdepth: 2

   neutron CLI <neutron>
   Network extensions to OpenStack Client <osc_plugins>
