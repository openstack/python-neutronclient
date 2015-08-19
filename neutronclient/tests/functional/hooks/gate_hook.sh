#!/usr/bin/env bash


set -ex

source $BASE/new/devstack-gate/functions.sh
start_timer

VENV=${1:-"functional"}


if [ "$VENV" == "functional-adv-svcs" ]
then
    export DEVSTACK_LOCAL_CONFIG="enable_plugin neutron-vpnaas git://git.openstack.org/openstack/neutron-vpnaas"
fi

remaining_time
timeout -s 9 ${REMAINING_TIME}m $BASE/new/devstack-gate/devstack-vm-gate.sh
