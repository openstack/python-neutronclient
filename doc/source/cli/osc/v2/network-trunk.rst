=============
network trunk
=============

A **network trunk** is a container to group logical ports from different
networks and provide a single trunked vNIC for servers. It consists of
one parent port which is a regular VIF and multiple subports which allow
the server to connect to more networks.

Network v2

network subport list
--------------------

List all subports for a given network trunk

.. program:: network subport list
.. code:: bash

    openstack network subport list
        --trunk <trunk>

.. option:: --trunk <trunk>

    List subports belonging to this trunk (name or ID) (required)

network trunk create
--------------------

Create a network trunk for a given project

.. program:: network trunk create
.. code:: bash

    openstack network trunk create
        --parent-port <parent-port>
        [--subport <port=,segmentation-type=,segmentation-id=>]
        [--enable | --disable]
        [--project <project> [--project-domain <project-domain>]]
        [--description <description>]
        <name>

.. option:: --parent-port <parent-port>

    Parent port belonging to this trunk (name or ID) (required)

.. option:: --subport <port=,segmentation-type=,segmentation-id=>

    Subport to add. Subport is of form 'port=<name or ID>,segmentation-type=,segmentation-ID='
    (--subport) option can be repeated

.. option:: --enable

    Enable trunk (default)

.. option:: --disable

    Disable trunk

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --description <description>

    A description of the trunk.

network trunk delete
--------------------

Delete a given network trunk

.. program:: network trunk delete
.. code:: bash

    openstack network trunk delete
        <trunk> [<trunk> ...]

.. _network_trunk_delete-trunk:
.. describe:: <trunk>

    Trunk(s) to delete (name or ID)

network trunk list
------------------

List all network trunks

.. program:: network trunk list
.. code:: bash

    openstack network trunk list
        [--long]

.. option:: --long

    List additional fields in output

network trunk set
-----------------

Set network trunk properties

.. program:: network trunk set
.. code:: bash

    openstack network trunk set
        [--name <name>]
        [--description <description>]
        [--subport <port=,segmentation-type=,segmentation-id=>]
        [--enable | --disable]
        <trunk>

.. option:: --name <name>

    Set trunk name

.. option:: --description <description>

    A description of the trunk.

.. option:: --subport <port=,segmentation-type=,segmentation-id=>

    Subport to add. Subport is of form 'port=<name or ID>,segmentation-type=,segmentation-ID='
    (--subport) option can be repeated

.. option:: --enable

    Enable trunk

.. option:: --disable

    Disable trunk

.. _network_trunk_set-trunk:
.. describe:: <trunk>

    Trunk to modify (name or ID)

network trunk show
------------------

Show information of a given network trunk

.. program:: network trunk show
.. code:: bash

    openstack network trunk show
        <trunk>

.. _network_trunk_show-trunk:
.. describe:: <trunk>

    Trunk to display (name or ID)

network trunk unset
-------------------

Unset subports from a given network trunk

.. program:: network trunk unset
.. code:: bash

    openstack network trunk unset
        --subport <subport>
        <trunk>

.. option:: --subport <subport>

    Subport to delete (name or ID of the port) (required)
    (--subport) option can be repeated

.. _network_trunk_unset-trunk:
.. describe:: <trunk>

    Unset subports from this trunk (name or ID)
