#!/usr/bin/env bash

set -ex

VENV=${1:-"functional"}

if [ "$VENV" == "functional-adv-svcs" ]
then
    export DEVSTACK_LOCAL_CONFIG="enable_plugin neutron-vpnaas git://git.openstack.org/openstack/neutron-vpnaas"
fi

$BASE/new/devstack-gate/devstack-vm-gate.sh
