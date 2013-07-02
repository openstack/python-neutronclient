Python bindings to the OpenStack Network API
============================================

In order to use the python neutron client directly, you must first obtain an auth token and identify which endpoint you wish to speak to. Once you have done so, you can use the API like so::

    >>> import logging
    >>> from neutronclient.neutron import client
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> neutron = client.Client('2.0', endpoint_url=OS_URL, token=OS_TOKEN)
    >>> neutron.format = 'json'
    >>> network = {'name': 'mynetwork', 'admin_state_up': True}
    >>> neutron.create_network({'network':network})
    >>> networks = neutron.list_networks(name='mynetwork')
    >>> print networks
    >>> network_id = networks['networks'][0]['id']
    >>> neutron.delete_network(network_id)


Command-line Tool
=================
In order to use the CLI, you must provide your OpenStack username, password, tenant, and auth endpoint. Use the corresponding configuration options (``--os-username``, ``--os-password``, ``--os-tenant-name``, and ``--os-auth-url``) or set them in environment variables::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_TENANT_NAME=tenant
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0

The command line tool will attempt to reauthenticate using your provided credentials for every request. You can override this behavior by manually supplying an auth token using ``--os-url`` and ``--os-auth-token``. You can alternatively set these environment variables::

    export OS_URL=http://neutron.example.org:9696/
    export OS_TOKEN=3bcc3d3a03f44e3d8377f9247b0ad155

If neutron server does not require authentication, besides these two arguments or environment variables (We can use any value as token.), we need manually supply ``--os-auth-strategy`` or set the environment variable::

    export OS_AUTH_STRATEGY=noauth

Once you've configured your authentication parameters, you can run ``neutron -h`` to see a complete listing of available commands.

Release Notes
=============

2.0
-----
* support Neutron API 2.0

2.2.0
-----
* add security group commands
* add Lbaas commands
* allow options put after positional arguments
* add NVP queue and net gateway commands
* add commands for agent management extensions
* add commands for DHCP and L3 agents scheduling
* support XML request format
* support pagination options

2.2.2
-----
* improved support for listing a large number of filtered subnets
* add --endpoint-type and OS_ENDPOINT_TYPE to shell client
* made the publicURL the default endpoint instead of adminURL
* add ability to update security group name (requires 2013.2-Havana or later)
* add flake8 and pbr support for testing and building
