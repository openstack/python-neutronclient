#!/bin/bash -xe

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script is executed inside post_test_hook function in devstack gate.

SCRIPTS_DIR="/usr/os-testr-env/bin/"

function generate_test_logs {
    local path="$1"
    # Compress all $path/*.txt files and move the directories holding those
    # files to /opt/stack/logs. Files with .log suffix have their
    # suffix changed to .txt (so browsers will know to open the compressed
    # files and not download them).
    if [ -d "$path" ]
    then
        sudo find $path -iname "*.log" -type f -exec mv {} {}.txt \; -exec gzip -9 {}.txt \;
        sudo mv $path/* /opt/stack/logs/
    fi
}

function generate_testr_results {
    # Give job user rights to access tox logs
    sudo -H -u $USER chmod o+rw .
    sudo -H -u $USER chmod o+rw -R .stestr
    if [ -f ".stestr/0" ] ; then
        .tox/$VENV/bin/subunit-1to2 < .stestr/0 > ./stestr.subunit
        $SCRIPTS_DIR/subunit2html ./stestr.subunit testr_results.html
        gzip -9 ./stestr.subunit
        gzip -9 ./testr_results.html
        sudo mv ./*.gz /opt/stack/logs/
    fi

    if [ "$venv" == "functional" ] || [ "$venv" == "functional-adv-svcs" ]
    then
        generate_test_logs "/tmp/${venv}-logs"
    fi
}

export NEUTRONCLIENT_DIR="$BASE/new/python-neutronclient"

sudo chown -R $USER:stack $NEUTRONCLIENT_DIR

# Go to the neutronclient dir
cd $NEUTRONCLIENT_DIR

# Run tests
VENV=${1:-"functional"}
echo "Running neutronclient functional test suite"
set +e
# Preserve env for OS_ credentials
sudo -E -H -u $USER tox -e $VENV
EXIT_CODE=$?
set -e

# Collect and parse result
generate_testr_results
exit $EXIT_CODE
