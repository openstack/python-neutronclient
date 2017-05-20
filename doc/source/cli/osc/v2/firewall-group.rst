==============
firewall group
==============

A **firewall group** is a perimeter firewall management to Networking.
Firewall group uses iptables to apply firewall policy to all VM ports and
router ports within a project.

Network v2

.. 'firewall group *' cannot be used below as it matches 'firewall group rule
   *' or 'firewall group policy *'.

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group create

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group delete

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group list

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group set

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group show

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group unset
