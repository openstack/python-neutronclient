======
bgpvpn
======

A **bgpvpn** resource contains a set of parameters to define a BGP-based VPN.
BGP-based IP VPNs networks are widely used in the industry especially for
enterprises. The networking BGP VPN project aims at supporting inter-connection
between L3VPNs and Neutron resources, i.e. Networks, Routers and Ports.

Network v2

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn create

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn delete

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn list

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn set

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn show

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn unset

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn network association *

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn router association *

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: bgpvpn port association *
