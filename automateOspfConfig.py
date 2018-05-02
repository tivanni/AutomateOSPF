#!/usr/bin/python
import netaddr
from netmiko import ConnectHandler

###Specify Username and Password
username = "admin"
password = "password"

###Specify info for ssh connection with netmiko
switch = {
    'device_type': 'cisco_ios',
    'username': username,
    'password': password,
}

###Creating dictionary for storing information
devices = {}
areas = {}
###Reading the config files
file_config = open('automateOspf.conf')

###Parsing the config file
for line in file_config:
    line = line.strip()  ###removes carriege return and similar characters
    if (line):  ###check line is not empty
        line_fields = line.split()
        first_field = line_fields[0]
        if(first_field == "device"):
            device_properties = {}
            device = line_fields[1]
            ip_address_mgmt = line_fields[2]
            ospf_process_number = line_fields[3]
            ospf_router_id = line_fields [4]
            device_properties['ip_address_mgmt'] = ip_address_mgmt
            device_properties['ospf_process_number'] = ospf_process_number
            device_properties['ospf_router_id'] = ospf_router_id
            devices[device] = device_properties
        elif(first_field == "area"):
            area = line_fields[1]
            network = netaddr.IPNetwork(line_fields[2])
            areas[area] = network


###Start devices configuration

hostnames = devices.keys()

for hostname in hostnames:
    ###The list area_to_configure will keep track of the area/s that need to be configured on the switch
    area_to_configure = []
    areas_list = areas.keys()
    #set the ip for the connection
    switch['ip'] = devices[hostname]['ip_address_mgmt']
    device_connect = ConnectHandler(**switch)
    output_ip_int_brief =device_connect.send_command ("show ip int brief")
    ###Reading the output of command executed.Output is in the following form
    '''R1#show ip interface brief
    Interface                  IP-Address      OK? Method Status                Protocol
    FastEthernet0/0            192.168.27.1    YES NVRAM  up                    up
    Serial0/0                  unassigned      YES NVRAM  administratively down down
    FastEthernet0/1            unassigned      YES manual administratively down down
    Serial0/1                  unassigned      YES NVRAM  administratively down down
    FastEthernet1/0            unassigned      YES unset  up                    up
    FastEthernet1/1            172.16.14.1     YES NVRAM  up                    up
    FastEthernet1/2            unassigned      YES unset  up                    down
    FastEthernet1/3            unassigned      YES unset  up                    down
    FastEthernet1/4            unassigned      YES unset  up                    down
    FastEthernet1/5            unassigned      YES unset  up                    down
    FastEthernet1/6            unassigned      YES unset  up                    down
    FastEthernet1/7            unassigned      YES unset  up                    down
    FastEthernet1/8            unassigned      YES unset  up                    down
    FastEthernet1/9            unassigned      YES unset  up                    down
    FastEthernet1/10           unassigned      YES unset  up                    down
    FastEthernet1/11           unassigned      YES unset  up                    down
    FastEthernet1/12           unassigned      YES unset  up                    down
    FastEthernet1/13           unassigned      YES unset  up                    down
    FastEthernet1/14           unassigned      YES unset  up                    down
    FastEthernet1/15           unassigned      YES unset  up                    down
    '''
    ###Analyzing output line per line
    output_ip_int_brief_lines = output_ip_int_brief.split("\n")
    for line in output_ip_int_brief_lines:
        line = line.strip()###removes carriege return and similar characters
        if (line):  ###check line is not empty
            line_fields = line.split()
            first_field = line_fields[0]
            ###check if the first field contains a valid interface name
            if (("Ethernet" in first_field) or ("Serial" in first_field)):
                interface_name = first_field
                interface_address = line_fields[1]
                ###check if the interface has an ip assigned
                if (interface_address != "unassigned"):
                    ip_address = netaddr.IPAddress(interface_address)
                    for area in areas_list:
                        if( (ip_address in areas[area]) and ( area not in area_to_configure )): ###if the interface has an ip address in one of the configured area, the area has to be configured in ospf
                           area_to_configure.append(area)

    print "Device " + hostname
    print "area_to_configure: " + str(area_to_configure)





