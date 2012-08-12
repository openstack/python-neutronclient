#!/bin/bash
set -x
function die() {
    local exitcode=$?
    set +o xtrace
    echo $@
    exit $exitcode
}


# test the CRUD of network
network=mynet1
quantum net-create $network || die "fail to create network $network"
temp=`quantum net-list -- --name $network --fields id | wc -l`
echo $temp
if [ $temp -ne 5 ]; then
   die "networks with name $network is not unique or found"
fi
network_id=`quantum net-list -- --name $network --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of network with name $network is $network_id"

quantum net-show $network ||  die "fail to show network $network"
quantum net-show $network_id ||  die "fail to show network $network_id"

quantum  net-update $network --admin_state_up False  ||  die "fail to update network $network"
quantum  net-update $network_id --admin_state_up True  ||  die "fail to update network $network_id"

quantum net-list -c id -- --id fakeid  || die "fail to list networks with column selection on empty list"

# test the CRUD of subnet
subnet=mysubnet1
cidr=10.0.1.3/24
quantum subnet-create $network $cidr --name $subnet  || die "fail to create subnet $subnet"
tempsubnet=`quantum subnet-list -- --name $subnet --fields id | wc -l`
echo $tempsubnet
if [ $tempsubnet -ne 5 ]; then
   die "subnets with name $subnet is not unique or found"
fi
subnet_id=`quantum subnet-list -- --name $subnet --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of subnet with name $subnet is $subnet_id"
quantum subnet-show $subnet ||  die "fail to show subnet $subnet"
quantum subnet-show $subnet_id ||  die "fail to show subnet $subnet_id"

quantum  subnet-update $subnet --dns_namesevers host1  ||  die "fail to update subnet $subnet"
quantum  subnet-update $subnet_id --dns_namesevers host2  ||  die "fail to update subnet $subnet_id"

# test the crud of ports
port=myport1
quantum port-create $network --name $port  || die "fail to create port $port"
tempport=`quantum port-list -- --name $port --fields id | wc -l`
echo $tempport
if [ $tempport -ne 5 ]; then
   die "ports with name $port is not unique or found"
fi
port_id=`quantum port-list -- --name $port --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of port with name $port is $port_id"
quantum port-show $port ||  die "fail to show port $port"
quantum port-show $port_id ||  die "fail to show port $port_id"

quantum  port-update $port --device_id deviceid1  ||  die "fail to update port $port"
quantum  port-update $port_id --device_id deviceid2  ||  die "fail to update port $port_id"
