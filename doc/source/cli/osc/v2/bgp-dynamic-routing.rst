===================
BGP Dynamic Routing
===================

BGP dynamic routing enables announcement of project subnet prefixes
via BGP. Admins create BGP speakers and BGP peers. BGP peers can be
associated with BGP speakers, thereby enabling peering sessions with
operator infrastructure. BGP speakers can be associated with networks,
which controls which routes are announced to peers.

Network v2

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker create

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker delete

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker list

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker set

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker show

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker show dragents

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker add network

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker remove network

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker add peer

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker remove peer

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp speaker list advertised routes

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp peer *

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgp dragent *
