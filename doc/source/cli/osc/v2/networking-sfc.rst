==============
networking sfc
==============

**Service Function Chaining** is a mechanism for overriding the basic destination based forwarding
that is typical of IP networks. Service Function Chains consist of an ordered sequence of
Service Functions (SFs). SFs are virtual machines (or potentially physical devices) that perform a
network function such as firewall, content cache, packet inspection, or any other function that
requires processing of packets in a flow from point A to point B even though the SFs are not
literally between point A and B from a routing table perspective.

Network v2

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc flow classifier *

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port chain *

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port pair create

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port pair delete

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port pair list

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port pair set

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port pair show

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc port pair group *

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: sfc service graph *
