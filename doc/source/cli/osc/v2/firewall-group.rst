==============
firewall group
==============

A **firewall group** is a perimeter firewall management to Networking.
Firewall group uses iptables to apply firewall policy to all VM ports and
router ports within a project.

Network v2

firewall group create
---------------------

Create a firewall group for a given project.

.. program:: firewall group create
.. code:: bash

    openstack firewall group create

.. _firewallgroup_create-firewallgroup:
.. option:: --name <name>

    Name for the firewall group.

.. option:: --enable

    Enable firewall group (default).

.. option:: --disable

    Disable firewall group.

.. option:: --public

    Make the firewall group public, which allows it to be used in all projects
    (as opposed to the default, which is to restrict its use to the current
    project).

.. option:: --private

    Restrict use of the firewall group to the current project.

.. option:: --project <project>

    Owner's project (name or ID).

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --description <description>

    A description of the firewall group.

.. option:: --ingress-firewall-policy <ingress-firewall-policy>

    Ingress firewall policy (name or ID).

.. option:: --no-ingress-firewall-policy

    Detach ingress firewall policy from the firewall group.

.. option:: --egress-firewall-policy <egress-firewall-policy>

    Egress firewall policy (name or ID).

.. option:: --no-egress-firewall-policy

    Detach egress firewall policy from the firewall group.

.. option:: --port <port>

    Port(s) to apply firewall group (name or ID).

.. option:: --no-port

    Detach all port from the firewall group.

firewall group delete
---------------------

Delete firewall group(s)

.. program:: firewall group delete
.. code:: bash

    openstack firewall group delete
        <firewall-group> [<firewall-group> ...]

.. _firewallgroup_delete-firewallgroup:
.. describe:: <firewall-group>

    Firewall group(s) to delete (name or ID).

firewall group list
-------------------

List all firewall groups

.. program:: firewall group list
.. code:: bash

    openstack firewall group list
        [--long]

.. option:: --long

    List additional fields in output.

firewall group set
------------------

Set firewall group properties

.. program:: firewall group set
.. code:: bash

    openstack firewall group set

.. _firewallgroup_set-firewallgroup:
.. describe:: <firewall-group>

    Firewall group to set (name or ID).

.. option:: --name <name>

    Set firewall group name.

.. option:: --enable

    Enable firewall group (default).

.. option:: --disable

    Disable firewall group.

.. option:: --public

    Make the firewall group public, which allows it to be used in all projects
    (as opposed to the default, which is to restrict its use to the current
    project).

.. option:: --private

    Restrict use of the firewall group to the current project.

.. option:: --description <description>

    A description of the firewall group.

.. option:: --ingress-firewall-policy <ingress-firewall-policy>

    Ingress firewall policy (name or ID).

.. option:: --no-ingress-firewall-policy

    Detach ingress firewall policy from the firewall group.

.. option:: --egress-firewall-policy

    Egress firewall policy (name or ID).

.. option:: --no-egress-firewall-policy

    Detach egress firewall policy from the firewall group.

.. option:: --port <port>

    Port(s) to apply firewall group.

.. option:: --no-port

    Detach all port from the firewall group.

firewall group show
-------------------

Show information of a given firewall group

.. program:: firewall group show
.. code:: bash

    openstack firewall group show
        <firewall-group>

.. _firewallgroup_show-firewallgroup:
.. describe:: <firewall-group>

    Firewall group to display (name or ID).

firewall group unset
--------------------

Unset firewall group properties

.. program:: firewall group unset
.. code:: bash

    openstack firewall group unset

.. _firewallgroup_unset-firewallgroup:
.. describe:: <firewall-group>

    Firewall group to unset (name or ID).

.. option:: --enable

    Disable firewall group.

.. option:: --public

    Restrict use of the firewall group to the current project.

.. option:: --ingress-firewall-policy

    Detach ingress firewall policy from the firewall group.

.. option:: --egress-firewall-policy

    Detach egress firewall policy from the firewall group.

.. option:: --port <port>

    Remove port(s) from the firewall group.

.. option:: --all-port

    Remove all ports from the firewall group.
