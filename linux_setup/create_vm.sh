#!/bin/bash

# Check if at least two arguments were provided
if [ $# -lt 2 ]
then
    echo "Please provide at least one number and password pair as arguments."
    exit 1
fi

# Convert the arguments into an array
args=("$@")

# Loop over the arguments two by two
for ((i=0; i<$#; i+=2))
do
    # Get the number and password
    number=${args[$i]}
    password=${args[$((i+1))]}
    
    echo "Creating VM with number: $number"

    # Create the VM and capture the output
    output=$(az vm create \
        --resource-group KoensSpeelzaal \
        --name airflowcursus-vm$number \
        --image Canonical:0001-com-ubuntu-server-jammy:22_04-lts:22.04.202301140 \
        --authentication-type password \
        --admin-username cursist$number \
        --admin-password $password \
        --os-disk-delete-option Delete \
        --size Standard_D2ds_v5 \
        --nic-delete-option Delete \
        --public-ip-sku Standard \
        --nsg-rule SSH)

    echo "VM airflowcursus-vm$number created."

    # Extract the public IP address and print it
    publicIpAddress=$(echo $output | jq -r '.publicIpAddress')
    echo "Public IP Address for VM airflowcursus-vm$number is: $publicIpAddress"

    # Open the port
    az vm open-port --resource-group KoensSpeelzaal --name airflowcursus-vm$number --port 3389 > /dev/null
    echo "Port 3389 opened for VM airflowcursus-vm$number."
done

echo "Script execution completed."