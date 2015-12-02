======================
Command-line Interface
======================

The **neutron** shell utility interacts with OpenStack Networking API from the
command-line. It supports the entire features of OpenStack Networking API.

Basic Usage
-----------

In order to use the CLI, you must provide your OpenStack username, password,
tenant, and auth endpoint. Use the corresponding configuration options
(``--os-username``, ``--os-password``, ``--os-tenant-name``, and
``--os-auth-url``), but it is easier to set them in environment variables.

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
