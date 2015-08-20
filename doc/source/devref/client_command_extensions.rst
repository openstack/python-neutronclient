=================================
Client command extension support
=================================

The client command extension adds support for extending the neutron client while
considering ease of creation.
Extensions strongly conform to preexisting neutron commands (/neutron/v2_0/).

A sample extension can be seen at:
neutronclient/neutron/v2_0/contrib/_fox_sockets.py

Minimum requirements from an extension
--------------------------------------

* Will have a class that subclasses NeutronClientExtension to provide the
  requisite version support, paths, and variable names for the client.
  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocket

* Will have at least one class that subclasses from the ClientExtension
  classes to provide the new functionality to the client
  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsList

* ClientExtension subclasses must have a shell_command class variable if the
  command is to be available to the CLI (shell.py)
  Example: neutronclient.neutron.v2_0.contrib._fox_sockets.FoxInSocketsList


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
setup.cfg under neutronclient.extension. For example:
[entry_points]
neutronclient.extension =
    fox_sockets = neutronclient.neutron.v2_0.contrib._fox_sockets