=======================
network onboard subnets
=======================

**network onboard subnets** enables a subnet to be adopted or
"onboarded" into an existing subnet pool. The CIDR of the subnet
is checked for uniqueness across any applicable address scopes
and all subnets allocated from the target subnet pool. Once
onboarded, the subnet CIDR is added to the prefix list of the
subnet pool and the subnet appears as though it has been allocated
from the subnet pool. The subnet also begins participating in the
applicable address scope if the subnet pool belongs to one.

Network v2

.. autoprogram-cliff:: openstack.neutronclient.v2
   :command: network onboard subnets
