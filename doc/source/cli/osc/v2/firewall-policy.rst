=====================
firewall group policy
=====================

A **firewall group policy** is an ordered collection of firewall rules.
A firewall policy can be shared across projects. Thus it can also be made part
of an audit workflow wherein the firewall_policy can be audited by the
relevant entity that is authorized (and can be different from the projects
which create or use the firewall group policy).

Network v2

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: firewall group policy *
