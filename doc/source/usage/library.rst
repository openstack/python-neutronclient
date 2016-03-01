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

.. code-block:: python

    >>> from neutronclient.v2_0 import client
    >>> neutron = client.Client(endpoint_url='http://192.168.206.130:9696/',
    ...                         token='d3f9226f27774f338019aa2611112ef6')

You can get ``X-Openstack-Request-Id`` as ``request_ids`` from the result.

.. code-block:: python

    >>> network = {'name': 'mynetwork', 'admin_state_up': True}
    >>> neutron.create_network({'network':network})
    >>> networks = neutron.list_networks(name='mynetwork')
    >>> print networks.request_ids
    ['req-978a0160-7ab0-44f0-8a93-08e9a4e785fa']
