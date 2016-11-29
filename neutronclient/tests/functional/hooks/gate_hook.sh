#!/usr/bin/env bash

set -ex

VENV=${1:-"functional"}

GATE_DEST=$BASE/new
NEUTRONCLIENT_PATH=$GATE_DEST/python-neutronclient
GATE_HOOKS=$NEUTRONCLIENT_PATH/neutronclient/tests/functional/hooks
DEVSTACK_PATH=$GATE_DEST/devstack

# Inject config from hook into localrc
function load_rc_hook {
    local hook="$1"
    config=$(cat $GATE_HOOKS/$hook)
    export DEVSTACK_LOCAL_CONFIG+="
# generated from hook '$hook'
${config}
"
}

if [ "$VENV" == "functional-adv-svcs" ]
then
    load_rc_hook fwaas
fi

$BASE/new/devstack-gate/devstack-vm-gate.sh
