#!/usr/bin/python
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
            device_properties['ip_address_mgmt'] = ip_address_mgmt
            device_properties['ospf_process_number'] = ospf_process_number
            devices[device] = device_properties
        elif(first_field == "area"):
            area = line_fields[1]
            network = line_fields[2]
            areas[area] = network


###Start devices configuration

hostnames = devices.keys()

for hostname in hostnames:
    #set the ip for the connection
    switch['ip'] = devices[hostname]['ip_address_mgmt']
    device_connect = ConnectHandler(**switch)
    output =device_connect.send_command ("show ip int brief")
    print output


