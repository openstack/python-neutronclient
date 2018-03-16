#!/usr/bin/env bash

set -ex

VENV=${1:-"functional"}

GATE_DEST=$BASE/new
NEUTRONCLIENT_PATH=$GATE_DEST/python-neutronclient
GATE_HOOKS=$NEUTRONCLIENT_PATH/neutronclient/tests/functional/hooks
DEVSTACK_PATH=$GATE_DEST/devstack
LOCAL_CONF=$DEVSTACK_PATH/late-local.conf
DSCONF=/tmp/devstack-tools/bin/dsconf

# Install devstack-tools used to produce local.conf; we can't rely on
# test-requirements.txt because the gate hook is triggered before neutronclient
# is installed
sudo -H pip install virtualenv
virtualenv /tmp/devstack-tools
/tmp/devstack-tools/bin/pip install -U devstack-tools==0.4.0

# Inject config from hook into localrc
function load_rc_hook {
    local hook="$1"
    local tmpfile
    local config
    tmpfile=$(tempfile)
    config=$(cat $GATE_HOOKS/$hook)
    echo "[[local|localrc]]" > $tmpfile
    $DSCONF setlc_raw $tmpfile "$config"
    $DSCONF merge_lc $LOCAL_CONF $tmpfile
    rm -f $tmpfile
}


if [ "$VENV" == "functional-adv-svcs" ]
then
    load_rc_hook fwaas
    load_rc_hook vpnaas
fi

export DEVSTACK_LOCALCONF=$(cat $LOCAL_CONF)
$BASE/new/devstack-gate/devstack-vm-gate.sh
