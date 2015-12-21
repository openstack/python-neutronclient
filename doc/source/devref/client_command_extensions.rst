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

Client command extension support
=================================

The client command extension adds support for extending the neutron client while
considering ease of creation.
Extensions strongly conform to preexisting neutron commands (/neutron/v2_0/).

A sample extension can be seen at:
neutronclient/neutron/v2_0/contrib/_fox_sockets.py

Minimum requirements from an extension
--------------------------------------

* NeutronClientExtension subclasses must have a shell_command class variable
  if the command is to be available to the CLI (shell.py)

  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsList

Minimum requirements to use canonical neutron CRUD commands framework
----------------------------------------------------------------------

Neutron commands are cliff commands, commands in extension can use their
own way to finish their tasks. But if they want to make use of the canonical
neutron CRUD commands framework, the extension should:

* have a class that subclasses NeutronClientExtension to provide the
  requisite resource name, version support, and resource collection and
  object paths for a resource the commands will process.

  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocket

* have a class that subclasses from the ClientExtensionList to provide
  resource object list function. This is because most commands
  need the list function to get object ID via
  neutronclient.neutron.v2_0.__init__.find_resource_by_id.

  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsList

* if needed, subclass ClientExtensionUpdate to implement update of the resource
  object.

  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsUpdate

* if needed, subclass ClientExtensionDelete to implement deletion of the resource
  object.

  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsDelete

* if needed, subclass ClientExtensionShow to get the detail of the resource
  object.

  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsShow

Precedence of command loading
------------------------------

* hard coded commands are loaded first
* external commands (installed in the environment) are loaded then

Commands that have the same name will be overwritten by commands that are
loaded later. To change the execution of a command for your particular
extension you only need to override the execute method.

Currently this extension support is limited to top-level resources.
Parent/child relationships may be added if desired.

neutronclient.extension entry_point
-----------------------------------

To activate the commands in a specific extension module, add an entry in
setup.cfg under neutronclient.extension. For example::

    [entry_points]
    neutronclient.extension =
        fox_sockets = neutronclient.neutron.v2_0.contrib._fox_sockets
