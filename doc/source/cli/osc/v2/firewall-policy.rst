=====================
firewall group policy
=====================

A **firewall group policy** is an ordered collection of firewall rules.
A firewall policy can be shared across projects. Thus it can also be made part
of an audit workflow wherein the firewall_policy can be audited by the
relevant entity that is authorized (and can be different from the projects
which create or use the firewall group policy).

Network v2

firewall group policy create
----------------------------

Create a firewall policy for a given project

.. program:: firewall group policy create
.. code:: bash

    openstack firewall group policy create

.. _firewallpolicy_create-firewallpolicy:
.. describe:: <name>

    Name for the firewall policy.

.. option:: --enable

    Enable firewall policy (default).

.. option:: --disable

    Disable firewall policy.

.. option:: --public

    Make the firewall policy public, which allows it to be used in all projects
    (as opposed to the default, which is to restrict its use to the current
    project).

.. option:: --private

    Restrict use of the firewall policy to the current project.

.. option:: --project <project>

    Owner's project (name or ID).

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --description <description>

    A description of the firewall policy.

.. option:: --firewall-rule <firewall-rule>

    Firewall rule(s) to apply (name or ID).

.. option:: --no-firewall-rule

    Remove all firewall rules from the firewall policy.

.. option:: --audited

    Enable auditing for the policy.

.. option:: --no-audited

    Disable auditing for the policy.


firewall group policy delete
----------------------------

Delete a given firewall policy

.. program:: firewall group policy delete
.. code:: bash

    openstack firewall group policy delete
        <firewall-policy> [<firewall-policy> ...]

.. _firewallpolicy_delete-firewallpolicy:
.. describe:: <firewall-policy>

    Firewall policy(s) to delete (name or ID).

firewall group policy list
--------------------------

List all firewall policies

.. program:: firewall group policy list
.. code:: bash

    openstack firewall group policy list
        [--long]

.. option:: --long

    List additional fields in output.

firewall group policy set
-------------------------

Set firewall policy properties

.. program:: firewall group policy set
.. code:: bash

    openstack firewall group policy set

.. _firewallpolicy_set-firewallpolicy:
.. describe:: <firewall-policy>

    Firewall policy to set (name or ID).

.. option:: --name <name>

    Set firewall policy name.

.. option:: --enable

    Enable firewall policy (default).

.. option:: --disable

    Disable firewall policy.

.. option:: --public

    Make the firewall policy public, which allows it to be used in all projects
    (as opposed to the default, which is to restrict its use to the current
    project).

.. option:: --private

    Restrict use of the firewall policy to the current project.

.. option:: --project <project>

    Owner's project (name or ID).

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --description <description>

    A description of the firewall policy.

.. option:: --firewall-rule <firewall-rule>

    Firewall rule(s) to apply (name or ID).

.. option:: --no-firewall-rule

    Unset all firewall rules from firewall policy.

.. option:: --audited

    Enable auditing for the policy.

.. option:: --no-audited

    Disable auditing for the policy.


firewall group policy show
--------------------------

Show information of a given firewall policy

.. program:: firewall group policy show
.. code:: bash

    openstack firewall group policy show
        <firewall-policy>

.. _firewallpolicy_show-firewallpolicy:
.. describe:: <firewall-policy>

    Firewall policy to display (name or ID).

firewall group policy unset
---------------------------

Unset firewall policy properties

.. program:: firewall group policy unset
.. code:: bash

    openstack firewall group policy unset

.. _firewallpolicy_unset-firewallpolicy:
.. describe:: <firewall-policy>

    Firewall policy to unset (name or ID).

.. option:: --enable

    Disable firewall policy.

.. option:: --public

    Restrict use of the firewall policy to the current project.

.. option:: --firewall-rule <firewall-rule>

    Firewall rule(s) to unset (name or ID).

.. option:: --all-firewall-rule

    Remove all firewall rules from the firewall policy.

.. option:: --audited

    Disable auditing for the policy.

firewall group policy add rule
------------------------------

Adds a firewall rule in a firewall policy relative to the position of other
rules.

.. program:: firewall group policy add rule
.. code:: bash

    openstack firewall group policy add rule
        <firewall-policy>
        <firewall-rule>

.. _firewallpolicy_add_rule-firewallpolicy:
.. describe:: <firewall-policy>

    Firewall policy to add rule (name or ID).

.. describe:: <firewall-rule>

    Firewall rule to be inserted (name or ID).

.. option:: --insert-after <firewall-rule>

    Insert the new rule after this existing rule (name or ID).

.. option:: --insert-before <firewall-rule>

    Insert the new rule before this existing rule (name or ID).

firewall group policy remove rule
---------------------------------

Removes a firewall rule from a firewall policy.

.. program:: firewall group policy remove rule
.. code:: bash

    openstack firewall group policy remove rule
        <firewall-policy>
        <firewall-rule>

.. _firewallpolicy_remove_rule-firewallpolicy:
.. describe:: <firewall-policy>

    Firewall policy to remove rule (name or ID).

.. describe:: <firewall-rule>

    Firewall rule to remove from policy (name or ID).
