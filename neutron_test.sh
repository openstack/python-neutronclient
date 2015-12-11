#!/bin/bash
set -x
function die() {
    local exitcode=$?
    set +o xtrace
    echo $@
    cleanup
    exit $exitcode
}

net_name=mynet1
subnet_name=mysubnet1
port_name=myport1
function cleanup() {
    echo Removing test port, subnet and net...
    neutron port-delete $port_name
    neutron subnet-delete $subnet_name
    neutron net-delete $net_name
}

noauth_tenant_id=me
if [ "$1" == "noauth" ]; then
    NOAUTH="--tenant_id $noauth_tenant_id"
else
    NOAUTH=
fi

echo "NOTE: User should be admin in order to perform all operations."
sleep 3

# test the CRUD of network
network=$net_name
neutron net-create $NOAUTH $network || die "fail to create network $network"
temp=`neutron net-list -- --name $network --fields id | wc -l`
echo $temp
if [ $temp -ne 5 ]; then
   die "networks with name $network is not unique or found"
fi
network_id=`neutron net-list -- --name $network --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of network with name $network is $network_id"

neutron net-show $network ||  die "fail to show network $network"
neutron net-show $network_id ||  die "fail to show network $network_id"

neutron  net-update $network --admin_state_up False  ||  die "fail to update network $network"
neutron  net-update $network_id --admin_state_up True  ||  die "fail to update network $network_id"

neutron net-list -c id -- --id fakeid  || die "fail to list networks with column selection on empty list"

# test the CRUD of subnet
subnet=$subnet_name
cidr=10.0.1.0/24
neutron subnet-create $NOAUTH $network $cidr --name $subnet  || die "fail to create subnet $subnet"
tempsubnet=`neutron subnet-list -- --name $subnet --fields id | wc -l`
echo $tempsubnet
if [ $tempsubnet -ne 5 ]; then
   die "subnets with name $subnet is not unique or found"
fi
subnet_id=`neutron subnet-list -- --name $subnet --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of subnet with name $subnet is $subnet_id"
neutron subnet-show $subnet ||  die "fail to show subnet $subnet"
neutron subnet-show $subnet_id ||  die "fail to show subnet $subnet_id"

neutron  subnet-update $subnet --dns_nameservers list=true 1.1.1.11 1.1.1.12  ||  die "fail to update subnet $subnet"
neutron  subnet-update $subnet_id --dns_nameservers list=true 2.2.2.21 2.2.2.22  ||  die "fail to update subnet $subnet_id"

# test the crud of ports
port=$port_name
neutron port-create $NOAUTH $network --name $port  || die "fail to create port $port"
tempport=`neutron port-list -- --name $port --fields id | wc -l`
echo $tempport
if [ $tempport -ne 5 ]; then
   die "ports with name $port is not unique or found"
fi
port_id=`neutron port-list -- --name $port --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of port with name $port is $port_id"
neutron port-show $port ||  die "fail to show port $port"
neutron port-show $port_id ||  die "fail to show port $port_id"
neutron  port-update $port --device_id deviceid1  ||  die "fail to update port $port"
neutron  port-update $port_id --device_id deviceid2  ||  die "fail to update port $port_id"
neutron  port-update $port_id --allowed-address-pair ip_address=1.1.1.11,mac_address=10:00:00:00:00:00 --allowed-address-pair ip_address=1.1.1.12,mac_address=10:00:00:00:00:01 ||  die "fail to update port $port_id --allowed-address-pair"
neutron port-show $port ||  die "fail to show port $port"
neutron port-show $port_id ||  die "fail to show port $port_id"
neutron  port-update $port_id --no-allowed-address-pairs ||  die "fail to update port $port_id --no-allowed-address-pairs"
neutron port-show $port ||  die "fail to show port $port"
neutron port-show $port_id ||  die "fail to show port $port_id"
neutron port-delete $port_id

# test the create port with allowed-address-pairs
port=$port_name
neutron port-create $NOAUTH $network --name $port -- --allowed-address-pairs type=dict list=true ip_address=1.1.1.11,mac_address=10:00:00:00:00:00 ip_address=1.1.1.12,mac_address=10:00:00:00:00:01 || die "fail to create port $port"
tempport=`neutron port-list -- --name $port --fields id | wc -l`
echo $tempport
if [ $tempport -ne 5 ]; then
   die "ports with name $port is not unique or found"
fi
port_id=`neutron port-list -- --name $port --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of port with name $port is $port_id"
neutron port-show $port ||  die "fail to show port $port"
neutron port-show $port_id ||  die "fail to show port $port_id"
neutron  port-update $port_id --no-allowed-address-pairs ||  die "fail to update port $port_id --no-allowed-address-pairs"
neutron  port-show $port_id

# test quota commands RUD
DEFAULT_NETWORKS=10
DEFAULT_PORTS=50
tenant_id=tenant_a
tenant_id_b=tenant_b
neutron quota-update --tenant_id $tenant_id --network 30 || die "fail to update quota for tenant $tenant_id"
neutron quota-update --tenant_id $tenant_id_b --network 20 || die "fail to update quota for tenant $tenant_id"
networks=`neutron quota-list -c network -c tenant_id | grep $tenant_id | awk '{print $2}'`
if [ $networks -ne 30 ]; then
   die "networks quota should be 30"
fi
networks=`neutron quota-list -c network -c tenant_id | grep $tenant_id_b | awk '{print $2}'`
if [ $networks -ne 20 ]; then
   die "networks quota should be 20"
fi
networks=`neutron quota-show --tenant_id $tenant_id | grep network | awk -F'|'  '{print $3}'`
if [ $networks -ne 30 ]; then
   die "networks quota should be 30"
fi
neutron quota-delete --tenant_id $tenant_id || die "fail to delete quota for tenant $tenant_id"
networks=`neutron quota-show --tenant_id $tenant_id | grep network | awk -F'|'  '{print $3}'`
if [ $networks -ne $DEFAULT_NETWORKS ]; then
   die "networks quota should be $DEFAULT_NETWORKS"
fi
# update self
if [ "t$NOAUTH" = "t" ]; then
    # with auth
    neutron quota-update --port 99 || die "fail to update quota for self"
    ports=`neutron quota-show | grep port | awk -F'|'  '{print $3}'`
    if [ $ports -ne 99 ]; then
       die "ports quota should be 99"
    fi

    ports=`neutron quota-list -c port | grep 99 | awk '{print $2}'`
    if [ $ports -ne 99 ]; then
       die "ports quota should be 99"
    fi
    neutron quota-delete || die "fail to delete quota for tenant self"
    ports=`neutron quota-show | grep port | awk -F'|'  '{print $3}'`
    if [ $ports -ne $DEFAULT_PORTS ]; then
       die "ports quota should be $DEFAULT_PORTS"
    fi
else
    # without auth
    neutron quota-update --port 100
    if [ $? -eq 0 ]; then
        die "without valid context on server, quota update command should fail."
    fi
    neutron quota-show
    if [ $? -eq 0 ]; then
        die "without valid context on server, quota show command should fail."
    fi
    neutron quota-delete
    if [ $? -eq 0 ]; then
        die "without valid context on server, quota delete command should fail."
    fi
    neutron quota-list || die "fail to update quota for self"
fi

cleanup
echo "Success! :)"

