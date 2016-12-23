======
bgpvpn
======

A **bgpvpn** resource contains a set of parameters to define a BGP-based VPN.
BGP-based IP VPNs networks are widely used in the industry especially for
enterprises. The networking BGP VPN project aims at supporting inter-connection
between L3VPNs and Neutron resources, i.e. Networks, Routers and Ports.

Network v2

bgpvpn create
-------------

Create a BGP VPN resource for a given project

.. program:: bgpvpn create
.. code:: bash

    openstack bgpvpn create

.. _bgpvpn_create-bgpvpn:
.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be used in case
    collisions between project names exist

.. option:: --name <name>

    Name for the BGP VPN.

.. option:: --route-target <route-target>

    Add Route Target to import list (repeat option for multiple Route Targets)

.. option:: --import-target <import-target>

    Add Route Target to import list (repeat option for multiple Route Targets)

.. option:: --export-target <export-target>

    Add Route Target to export list (repeat option for multiple RouteTargets)

.. option:: --route-distinguisher <route-distinguisher>

    Add Route Distinguisher to the list of Route Distinguishers from which a
    Route Distinguishers will be picked from to advertise a VPN route (repeat
    option for multiple Route Distinguishers)

.. option:: --type {l2,l3}

    BGP VPN type selection between IP VPN (l3) and Ethernet VPN (l2)
    (default: l3)

bgpvpn set
----------

Set BGP VPN properties

.. program:: bgpvpn set
.. code:: bash

    openstack bgpvpn set

.. _bgpvpn_set-bgpvpn:
.. describe:: <bgpvpn>

    BGP VPN to update (name or ID)

.. option:: --name <name>

    Name for the BGP VPN

.. option:: --route-target <route-target>

    Add Route Target to import list (repeat option for multiple Route Targets)

.. option:: --no-route-target

    Empty route target list.

.. option:: --import-target <import-target>

    Add Route Target to import list (repeat option for multiple Route Targets)

.. option:: --no-import-target

    Empty import route target list

.. option:: --export-target <export-target>

    Add Route Target to export list (repeat option for multiple Route Targets)

.. option:: --no-export-target

    Empty export route target list

.. option:: --route-distinguisher <route-distinguisher>

    Add Route Distinguisher to the list of Route Distinguishers from which a
    Route Distinguishers will be picked from to advertise a VPN route (repeat
    option for multiple Route Distinguishers)

.. option:: --no-route-distinguisher

    Empty route distinguisher list

bgpvpn unset
----------

Unset BGP VPN properties

.. program:: bgpvpn unset
.. code:: bash

    openstack bgpvpn unset

.. _bgpvpn_unset-bgpvpn:
.. describe:: <bgpvpn>

    BGP VPN to update (name or ID)

.. option:: --route-target <route-target>

    Remove Route Target from import/export list (repeat option for multiple
    Route Targets)

.. option:: --all-route-target

    Empty route target list

.. option:: --import-target <import-target>

    Remove Route Target from import list (repeat option for multiple Route
    Targets)

.. option:: --all-import-target

    Empty import route target list

.. option:: --export-target <export-target>

    Remove Route Target from export list (repeat option for multiple Route
    Targets)

.. option:: --all-export-target

    Empty export route target list

.. option:: --route-distinguisher <route-distinguisher>

    Remove Route Distinguisher from the list of Route Distinguishers from which
    a Route Distinguishers will be picked from to advertise a VPN route
    (repeat option for multiple Route Distinguishers)

.. option:: --all-route-distinguisher

    Empty route distinguisher list

bgpvpn delete
-------------

Delete BGP VPN resource(s)

.. program:: bgpvpn delete
.. code:: bash

    openstack bgpvpn delete
        <bgpvpn> [<bgpvpn> ...]

.. _bgpvpn_delete-bgpvpn:
.. describe:: <bgpvpn>
    BGP VPN(s) to delete (name or ID)

bgpvpn list
-----------

List BGP VPN resources

.. program:: bgpvpn list
.. code:: bash

    openstack bgpvpn list

.. _bgpvpn_list-bgpvpn:
.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be used in case
    collisions between project names exist.

.. option:: --long

    List additional fields in output

.. option:: --property <key=value>

    Filter property to apply on returned BGP VPNs (repeat to filter on multiple
    properties)

bgpvpn show
-----------

Show information of a given BGP VPN

.. program:: bgpvpn show
.. code:: bash

    openstack bgpvpn show

.. _bgpvpn_show-bgpvpn:
.. describe:: <bgpvpn>

    BGP VPN to display (name or ID)

bgpvpn network association create
---------------------------------

Create a BGP VPN network association

.. program:: bgpvpn network association create
.. code:: bash

    openstack bgpvpn network association create

.. _bgpvpn_net-assoc_create-bgpvpn:
.. describe:: <bgpvpn>

    ID or name of the BGP VPN

.. describe:: <network>

    ID or name of the network

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be used in case
    collisions between project names exist.

bgpvpn network association delete
---------------------------------

Remove a BGP VPN network association(s) for a given BGP VPN

.. program:: bgpvpn network association delete
.. code:: bash

    openstack bgpvpn network association delete
    <network association>[<network association> ...] <bgpvpn>

.. _bgpvpn_net-assoc_delete-bgpvpn:
.. describe:: <network association>
    ID(s) of the network association(s) to remove

.. describe:: <bgpvpn>
    ID or name of the BGP VPN

bgpvpn network association list
-------------------------------

List BGP VPN network associations for a given BGP VPN

.. program:: bgpvpn network association list
.. code:: bash

    openstack bgpvpn network association list

.. _bgpvpn_net-assoc_list-bgpvpn:
.. describe:: <bgpvpn>
    ID or name of the BGP VPN

.. option:: --long

    List additional fields in output

bgpvpn network association show
-------------------------------

Show information of a given BGP VPN network association

.. program:: bgpvpn network association show
.. code:: bash

    openstack bgpvpn network association show

.. _bgpvpn_net-assoc_show-bgpvpn:
.. describe:: <network association>
    ID of the network association to look up

.. describe:: <bgpvpn>
    BGP VPN the association belongs to (name or ID)

bgpvpn router association create
--------------------------------

Create a BGP VPN router association

.. program:: bgpvpn router association create
.. code:: bash

    openstack bgpvpn router association create

.. _bgpvpn_router-assoc_create-bgpvpn:
.. describe:: <bgpvpn>

    ID or name of the BGP VPN

.. describe:: <router>

    ID or name of the router.

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be used in case
    collisions between project names exist.

bgpvpn router association delete
--------------------------------

Delete a BGP VPN router association(s) for a given BGP VPN

.. program:: bgpvpn router association delete
.. code:: bash

    openstack bgpvpn router association delete
    <router association>[<router association> ...] <bgpvpn>

.. _bgpvpn_router-assoc_delete-bgpvpn:
.. describe:: <router association>
    ID(s) of the router association(s) to delete.

.. describe:: <bgpvpn>
    ID or name of the BGP VPN

bgpvpn router association list
------------------------------

List BGP VPN router associations for a given BGP VPN

.. program:: bgpvpn router association list
.. code:: bash

    openstack bgpvpn router association list

.. _bgpvpn_router-assoc_list-bgpvpn:
.. describe:: <bgpvpn>
    ID or name of the BGP VPN

.. option:: --long

    List additional fields in output

bgpvpn router association show
------------------------------

Show information of a given BGP VPN router association

.. program:: bgpvpn router association show
.. code:: bash

    openstack bgpvpn router association show

.. _bgpvpn_router-assoc_show-bgpvpn:
.. describe:: <router association>
    ID of the router association to look up

.. describe:: <bgpvpn>
    BGP VPN the association belongs to (name or ID)