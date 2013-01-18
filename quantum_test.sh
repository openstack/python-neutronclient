#!/bin/bash
set -x
function die() {
    local exitcode=$?
    set +o xtrace
    echo $@
    exit $exitcode
}

noauth_tenant_id=me
if [ $1 == 'noauth' ]; then
    NOAUTH="--tenant_id $noauth_tenant_id"
else
    NOAUTH=
fi

FORMAT=" --request-format xml"

# test the CRUD of network
network=mynet1
quantum net-create $FORMAT $NOAUTH $network || die "fail to create network $network"
temp=`quantum net-list $FORMAT -- --name $network --fields id | wc -l`
echo $temp
if [ $temp -ne 5 ]; then
   die "networks with name $network is not unique or found"
fi
network_id=`quantum net-list -- --name $network --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of network with name $network is $network_id"

quantum net-show $FORMAT $network ||  die "fail to show network $network"
quantum net-show $FORMAT $network_id ||  die "fail to show network $network_id"

quantum  net-update $FORMAT $network --admin_state_up False  ||  die "fail to update network $network"
quantum  net-update $FORMAT $network_id --admin_state_up True  ||  die "fail to update network $network_id"

quantum net-list $FORMAT -c id -- --id fakeid  || die "fail to list networks with column selection on empty list"

# test the CRUD of subnet
subnet=mysubnet1
cidr=10.0.1.3/24
quantum subnet-create $FORMAT $NOAUTH $network $cidr --name $subnet  || die "fail to create subnet $subnet"
tempsubnet=`quantum subnet-list $FORMAT -- --name $subnet --fields id | wc -l`
echo $tempsubnet
if [ $tempsubnet -ne 5 ]; then
   die "subnets with name $subnet is not unique or found"
fi
subnet_id=`quantum subnet-list $FORMAT -- --name $subnet --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of subnet with name $subnet is $subnet_id"
quantum subnet-show $FORMAT $subnet ||  die "fail to show subnet $subnet"
quantum subnet-show $FORMAT $subnet_id ||  die "fail to show subnet $subnet_id"

quantum  subnet-update $FORMAT $subnet --dns_namesevers host1  ||  die "fail to update subnet $subnet"
quantum  subnet-update $FORMAT $subnet_id --dns_namesevers host2  ||  die "fail to update subnet $subnet_id"

# test the crud of ports
port=myport1
quantum port-create $FORMAT $NOAUTH $network --name $port  || die "fail to create port $port"
tempport=`quantum port-list $FORMAT -- --name $port --fields id | wc -l`
echo $tempport
if [ $tempport -ne 5 ]; then
   die "ports with name $port is not unique or found"
fi
port_id=`quantum port-list $FORMAT -- --name $port --fields id | tail -n 2 | head -n 1 |  cut -d' ' -f 2`
echo "ID of port with name $port is $port_id"
quantum port-show $FORMAT $port ||  die "fail to show port $port"
quantum port-show $FORMAT $port_id ||  die "fail to show port $port_id"

quantum  port-update $FORMAT $port --device_id deviceid1  ||  die "fail to update port $port"
quantum  port-update $FORMAT $port_id --device_id deviceid2  ||  die "fail to update port $port_id"

# test quota commands RUD
DEFAULT_NETWORKS=10
DEFAULT_PORTS=50
tenant_id=tenant_a
tenant_id_b=tenant_b
quantum quota-update $FORMAT --tenant_id $tenant_id --network 30 || die "fail to update quota for tenant $tenant_id"
quantum quota-update $FORMAT --tenant_id $tenant_id_b --network 20 || die "fail to update quota for tenant $tenant_id"
networks=`quantum quota-list $FORMAT -c network -c tenant_id | grep $tenant_id | awk '{print $2}'`
if [ $networks -ne 30 ]; then
   die "networks quota should be 30"
fi
networks=`quantum quota-list $FORMAT -c network -c tenant_id | grep $tenant_id_b | awk '{print $2}'`
if [ $networks -ne 20 ]; then
   die "networks quota should be 20"
fi
networks=`quantum quota-show $FORMAT --tenant_id $tenant_id | grep network | awk -F'|'  '{print $3}'`
if [ $networks -ne 30 ]; then
   die "networks quota should be 30"
fi
quantum quota-delete $FORMAT --tenant_id $tenant_id || die "fail to delete quota for tenant $tenant_id"
networks=`quantum quota-show $FORMAT --tenant_id $tenant_id | grep network | awk -F'|'  '{print $3}'`
if [ $networks -ne $DEFAULT_NETWORKS ]; then
   die "networks quota should be $DEFAULT_NETWORKS"
fi
# update self
if [ "t$NOAUTH" = "t" ]; then
    # with auth
    quantum quota-update $FORMAT --port 99 || die "fail to update quota for self"
    ports=`quantum quota-show $FORMAT | grep port | awk -F'|'  '{print $3}'`
    if [ $ports -ne 99 ]; then
       die "ports quota should be 99"
    fi
    
    ports=`quantum quota-list $FORMAT -c port | grep 99 | awk '{print $2}'`
    if [ $ports -ne 99 ]; then
       die "ports quota should be 99"
    fi
    quantum quota-delete $FORMAT || die "fail to delete quota for tenant self"
    ports=`quantum quota-show $FORMAT | grep port | awk -F'|'  '{print $3}'`
    if [ $ports -ne $DEFAULT_PORTS ]; then
       die "ports quota should be $DEFAULT_PORTS"
    fi
else
    # without auth
    quantum quota-update $FORMAT --port 100
    if [ $? -eq 0 ]; then
        die "without valid context on server, quota update command should fail."
    fi
    quantum quota-show $FORMAT
    if [ $? -eq 0 ]; then
        die "without valid context on server, quota show command should fail."
    fi
    quantum quota-delete $FORMAT
    if [ $? -eq 0 ]; then
        die "without valid context on server, quota delete command should fail."
    fi
    quantum quota-list $FORMAT || die "fail to update quota for self"
fi
