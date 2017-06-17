===================
firewall group rule
===================

A **firewall group rule** represents a collection of attributes like ports, IP
addresses which define match criteria and action (allow, or deny) that needs to
be taken on the matched data traffic.

Network v2

firewall group rule create
--------------------------

Create a firewall rule for a given project

.. program:: firewall group rule create
.. code:: bash

    openstack firewall group rule create

.. option:: --name <name>

    Set firewall rule name.

.. option:: --enable

    Enable firewall rule (default).

.. option:: --disable

    Disable firewall rule.

.. option:: --public

    Make the firewall rule public, which allows it to be used in all projects
    (as opposed to the default, which is to restrict its use to the current
    project).

.. option:: --private

    Restrict use of the firewall rule to the current project.

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --description <description>

    A description of the firewall rule.

.. option:: --protocol <protocol>

    Protocol for the firewall rule ('tcp', 'udp', 'icmp', 'any').
    Default is 'any'.

.. option:: --action <action>

    Action for the firewall rule ('allow', 'deny', 'reject').
    Default is 'deny'.

.. option:: --ip-version <ip-version>

    Set IP version 4 or 6 (default is 4).

.. option:: --source-port <source-port>

    Source port number or range
    (integer in [1, 65535] or range like 123:456).

.. option:: --no-source-port

    Detach source port number or range.

.. option:: --destination-port <destination-port>

    Destination port number or range
    (integer in [1, 65535] or range like 123:456).

.. option:: --no-destination-port

    Detach destination port number or range.

.. option:: --source-ip-address <source-ip-address>

    Source IP address or subnet.

.. option:: --no-source-ip-address

    Detach source IP address.

.. option:: --destination-ip-address <destination-ip-address>

    Destination IP address or subnet.

.. option:: --no-destination-ip-address

    Detach destination IP address.

.. option:: --enable-rule

    Enable this rule (default is enabled).

.. option:: --disable-rule

    Disable this rule.

firewall group rule delete
--------------------------

Delete a given firewall rule

.. program:: firewall group rule delete
.. code:: bash

    openstack firewall group rule delete
        <firewall-rule> [<firewall-rule> ...]

.. _firewallrule_delete-firewallrule:
.. describe:: <firewall-rule>

    Firewall rule(s) to delete (name or ID).

firewall group rule list
------------------------

List all firewall rules

.. program:: firewall group rule list
.. code:: bash

    openstack firewall group rule list
        [--long]

.. option:: --long

    List additional fields in output.

firewall group rule set
-----------------------

Set firewall rule properties

.. program:: firewall group rule set
.. code:: bash

    openstack firewall group rule set

.. _firewallrule_set-firewallrule:
.. describe:: <firewall-rule>

    Firewall rule to set (name or ID).

.. option:: --name <name>

    Set firewall rule name.

.. option:: --enable

    Enable firewall rule (default).

.. option:: --disable

    Disable firewall rule.

.. option:: --public

    Make the firewall rule public, which allows it to be used in all projects
    (as opposed to the default, which is to restrict its use to the current
    project).

.. option:: --private

    Restrict use of the firewall rule to the current project.

.. option:: --project <project>

    Owner's project (name or ID).

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --description <description>

    A description of the firewall rule.

.. option:: --protocol <protocol>

    Protocol for the firewall rule ('tcp', 'udp', 'icmp', 'any').

.. option:: --action <action>

    Action for the firewall rule ('allow', 'deny', 'reject').

.. option:: --ip-version <ip-version>

    Set IP version 4 or 6 (default is 4).

.. option:: --source-port <source-port>

    Source port number or range
    (integer in [1, 65535] or range like 123:456).

.. option:: --no-source-port

    Detach source port number or range.

.. option:: --destination-port <destination-port>

    Destination port number or range
    (integer in [1, 65535] or range like 123:456).

.. option:: --no-destination-port

    Detach destination port number or range.

.. option:: --source-ip-address <source-ip-address>

    Source IP address or subnet.

.. option:: --no-source-ip-address

    Detach source IP address.

.. option:: --destination-ip-address <destination-ip-address>

    Destination IP address or subnet.

.. option:: --no-destination-ip-address

    Detach destination IP address.

.. option:: --enable-rule

    Enable this rule (default is enabled).

.. option:: --disable-rule

    Disable this rule.

firewall group rule show
------------------------

Show information of a given firewall rule

.. program:: firewall group rule show
.. code:: bash

    openstack firewall group rule show
        <firewall-rule>

.. _firewallrule_show-firewallrule:
.. describe:: <firewall-rule>

    Firewall rule to display (name or ID).

firewall group rule unset
-------------------------

Unset firewall rule properties

.. program:: firewall group rule unset
.. code:: bash

    openstack firewall group rule unset

.. _firewallrule_unset-firewallrule:
.. describe:: <firewall-rule>

    Firewall rule to unset (name or ID).

.. option:: --enable

    Disable firewall rule.

.. option:: --public

    Restrict use of the firewall rule to the current project.

.. option:: --source-port

    Detach source port number or range.

.. option:: --destination-port

    Detach destination port number or range.

.. option:: --source-ip-address

    Detach source IP address.

.. option:: --destination-ip-address

    Detach destination IP address.

.. option:: --enable-rule

    Disable this rule.
