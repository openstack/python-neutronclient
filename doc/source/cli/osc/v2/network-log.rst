===========
network log
===========

A **network log** is a container to group security groups or ports for logging.
Specified resources can be logged via these event (``ALL``, ``ACCEPT`` or
``DROP``).

Network v2

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: network loggable resources list

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: network log *
