# Name: launch-vbox.py
# Author: Dave Randall <dave@randall-it.uk>
# Created: 2017-05-25
# Modified: 2017-05-25
# Description: Imports a vbox .ovf and runs Chef on it

# NOTE: You need to be in a Chef configured folder in order to use knife

# Header
from subprocess import call, check_output # Allows calling shell commands
import time # For waiting

# Parameters
ovf_file_name = "packer-virtualbox-iso-1499018864"
vm_name = "jenkins-02"
role = "role[centos-general]"

print(vm_name + " will be built from " + ovf_file_name + " and configured by Chef with " + role)

# Determine variables
ovf_file_path = "/home/dave/repos/packer/templates/output-virtualbox-iso/" + ovf_file_name + ".ovf"

# Launch a VM using the OVF (https://www.virtualbox.org/manual/ch08.html#vboxmanage-export)
call(["VBoxManage", "import", ovf_file_path, "--vsys", "0", "--vmname", vm_name])

# Set NIC to bridged
call(["VBoxManage", "modifyvm", vm_name, "--nic1", "bridged", "--bridgeadapter1", "wlp3s0"])

# Start the VM
call(["VBoxManage", "startvm", vm_name, "--type", "headless"])

# Loop until IP address is found
result = check_output(["VBoxManage", "guestproperty", "get", vm_name, "/VirtualBox/GuestInfo/Net/0/V4/IP"])
print(result)
while result == 'No value set!\n':

    # Get VM info to determine IP address
    print("Waiting for IP address")
    result = check_output(["VBoxManage", "guestproperty", "get", vm_name, "/VirtualBox/GuestInfo/Net/0/V4/IP"])
    time.sleep(60)

# Bootstrap the node with Chef
ip = result.replace("Value: ", "")
print("Running chef on " + ip)
call(["knife", "bootstrap", ip, "-N", vm_name, "-x", "root", "-P", "packer", "-r", role, "--sudo"])
