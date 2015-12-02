========================
neutronclient Python API
========================

Basic Usage
-----------

First create a client instance.

.. code-block:: python

    >>> from neutronclient.v2_0 import client
    >>> username='adminUser'
    >>> password='secretword'
    >>> tenant_name='openstackDemo'
    >>> auth_url='http://192.168.206.130:5000/v2.0'
    >>> neutron = client.Client(username=username,
    ...                         password=password,
    ...                         tenant_name=tenant_name,
    ...                         auth_url=auth_url)

Now you can call various methods on the client instance.

.. code-block:: python

    >>> network = {'name': 'mynetwork', 'admin_state_up': True}
    >>> neutron.create_network({'network':network})
    >>> networks = neutron.list_networks(name='mynetwork')
    >>> print networks
    >>> network_id = networks['networks'][0]['id']
    >>> neutron.delete_network(network_id)

Alternatively, you can create a client instance using an auth token
and a service endpoint URL directly.

    >>> from neutronclient.v2_0 import client
    >>> neutron = client.Client(endpoint_url='http://192.168.206.130:9696/',
                                token='d3f9226f27774f338019aa2611112ef6')
