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

CLI Option Guideline
====================

This document describes the conventions of neutron CLI options.

General conventions
-------------------

#. Option names should be delimited by a hyphen instead of a underscore.
   This is the common guidelines across all OpenStack CLIs.

   * Good: ``--ip-version``
   * Not Good: ``--ip_version``

#. Use at least one required option for ``*-create`` command.  If all options
   are optional, we typically use ``name`` field as a required option.

#. When you need to specify an ID of a resource, it is better to provide
   another way to specify the resource like ``name`` or other reasonable field.

#. If an attribute name in API is ``foo_id``, the corresponding option
   should be ``--foo`` instead of ``--foo-id``.

   * It is because we usually support ID and ``name`` to specify a resource.

#. Do not use ``nargs='?'`` without a special reason.

   * The behavior of ``nargs='?'`` option for python argparse is
     bit tricky and may lead to unexpected option parsing different
     from the help message. The detail is described in the
     :ref:`Background section <background-nargs>` below.

#. (option) Avoid using positional options as much as possible.

   * Positional arguments should be limited to attributes which will
     be required in the long future.

#. We honor existing options and should keep compatibilities when adding or
   changing options.

Options for boolean value
-------------------------

Use the form of ``--option-name {True|False}``.

* For a new option, it is recommended.
* It is suggested to use ``common.utils.add_boolean_argument`` in an
  implementation. It allows ``true``/``false`` in addition to ``True``/``False``.
* For existing options, migration to the recommended form is not necessarily
  required. All backward-compatibility should be kept without reasonable
  reasons.

Options for dict value
----------------------

Some API attributes take a dictionary.

``--foo key1=val1,key2=val2`` is usually used.

This means ``{"key1": "val1", "key2": "val2"}`` is passed in the API layer.

Examples:

* ``--host-route destination=CIDR,nexthop=IP_ADDR`` for a subnet
* ``--fixed-ip subnet_id=SUBNET,ip_address=IP_ADDR`` for a port.

Options for list value
----------------------

Some attributes take a list.

In this case, we usually use:

* Define an option per element (Use a singular form as an option name)
* Allow to specify the option multiple times

For Example, **port-create** has ``--security-group`` option.
``--security-group SG1 --security-group SG2`` generates
``{"security_groups: ["SG1", "SG2"]}`` in the API layer.

This convention applies to a case of a list of dict.
``--allocation-pool`` and ``--host-route`` for a subnet are examples.

Compatibility with extra arguments
----------------------------------

*extra arguments* supports various types of option specifications.
At least the following patterns needs to be considered when defining
a new option. For more detail, see :ref:`cli_extra_arguments`.

* Normal options with value
* Boolean options : ``--foo True``, ``--bar=False``
* List options : ``--bars list=true val1 val2``, ``--bars val1 val2``
* Dict options : ``--foo type=dict key1=va1,key2=val2``
* List of Dict options : ``--bars list=true type=dict key1=val1,key2=val2 key3=val3,key4=val4``
* ``action=clear``

For normal options with value, there are four patterns to specify an option
as extra arguments.

* ``--admin-state-up True`` (a space between option name and value)
* ``--admin-state-up=True`` (= between option name and value)
* ``--admin_state_up True`` (underscore is used as delimiter)
* ``--admin_state_up=True`` (underscore is used as delimiter)

.. _background:

Background
----------

There are a lot of opinions on which form of options are better or not.
This section tries to capture the reason of the current choice.

Use at least one required option
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a convention, **neutron** CLI requires one required argument.

If all options are optional in the API level and we have ``name`` field,
we usually use ``name`` as a required parameter.
Requiring at least one argument has the following benefits:

* If we run ``neutron *-create`` without a required argument, we will have a
  brief help message without detail option help. It is convenient.
* We can avoid miss operation by just hitting ``neutron *-create``.
  Requiring at least one parameter is a good balance.

Even though we can change this convention to allow to create a resource
without ``name`` field, it will bring confusions to existing users.

There may be opinion that it is inconsistent with API level requirement
or Horizon behavior, but even if neutron CLI requires ``name`` field
there is no bad impact on regular users. Considering possible confusion
if we change it, it looks better to keep it as-is.

Options for Boolean value
~~~~~~~~~~~~~~~~~~~~~~~~~

* ``--enable-foo``/``--disable-foo`` or similar patterns (including
  ``--admin-state-down``) is not suggested because we need two exclusive
  options for one attribute in REST API. It is meaningless.

* It is not recommended to have an option only to specify non-default value.
  For example, we have ``--shared`` or ``--admin-state-down`` options for
  net-create.  This form only works for ``*-create`` and does not work for
  ``*-update``.  It leads to having different options for ``*-create`` and
  ``*-update``.

* A flag option like ``--enable-dhcp`` (without value) also has a problem when
  considering the compatibility with *extra argument*.  We can specify
  ``-enable-dhcp True/False`` or ``--enable-dhcp=True/False`` in the *extra
  argument* mechanism. If we introduce ``--enable-dhcp`` (without value),
  the form of ``-enable-dhcp True/False`` cannot be used now.
  This is another reason we don't use a flag style option for a boolean parameter.

.. _background-nargs:

Avoid using nargs in positional or optional arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The behavior of ``nargs='?'`` option for python argparse is bit tricky.
When we use ``nargs='?'`` and if the order of command-line options is
changed then the command-line parser may fail to parse the arguments
correctly. Two examples of such failures are provided below.

Example 1:
This example shows how the actual behavior can differ from the provided
help message. In the below block, help message at ``[5]`` says ``--bb CC``
is a valid format but the argument parsing for the same format fails at ``[7]``.

.. code-block:: console

   In [1]: import argparse
   In [2]: parser = argparse.ArgumentParser()
   In [3]: parser.add_argument('--bb', nargs='?')
   In [4]: parser.add_argument('cc')

   In [5]: parser.print_help()
   usage: ipython [-h] [--bb [BB]] cc

   positional arguments:
     cc

   optional arguments:
     -h, --help  show this help message and exit
     --bb [BB]

   In [6]: parser.parse_args('--bb 1 X'.split())
   Out[6]: Namespace(bb='1', cc='X')

   In [7]: parser.parse_args('--bb X'.split())
   usage: ipython [-h] [--bb [BB]] cc
   ipython: error: too few arguments
   An exception has occurred, use %tb to see the full traceback.

   SystemExit: 2


Example 2:
This example shows how fragile ``nargs='?'`` can be when user specifies
options in different order from the help message.

.. code-block:: console

   In [1]: import argparse
   In [2]: parser = argparse.ArgumentParser()
   In [3]: parser.add_argument('--a', help='option a')
   In [4]: parser.add_argument('--b', help='option b')
   In [5]: parser.add_argument('x', help='positional arg X')
   In [6]: parser.add_argument('y', nargs='?', help='positional arg Y')
   In [7]: parser.print_help()
   usage: ipython [-h] [--a A] [--b B] x [y]

   positional arguments:
     x           positional arg X
     y           positional arg Y

   optional arguments:
     -h, --help  show this help message and exit
     --a A       option a
     --b B       option b

   In [8]: parser.parse_args('--a 1 --b 2 X Y'.split())
   Out[8]: Namespace(a='1', b='2', x='X', y='Y')

   In [9]: parser.parse_args('X Y --a 1 --b 2'.split())
   Out[9]: Namespace(a='1', b='2', x='X', y='Y')

   In [10]: parser.parse_args('X --a 1 --b 2 Y'.split())
   usage: ipython [-h] [--a A] [--b B] x [y]
   ipython: error: unrecognized arguments: Y
   An exception has occurred, use %tb to see the full traceback.

   SystemExit: 2

   To exit: use 'exit', 'quit', or Ctrl-D.
   To exit: use 'exit', 'quit', or Ctrl-D.

Note: Most CLI users don't care about the order of the command-line
options. Hence, such fragile behavior should be avoided.

