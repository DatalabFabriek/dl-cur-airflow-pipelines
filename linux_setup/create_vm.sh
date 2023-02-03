az vm create \
    --resource-group KoensSpeelzaal \
    --name airflowcursus-vm4 \
    --image Canonical:0001-com-ubuntu-server-jammy:22_04-lts:22.04.202301140 \
    --authentication-type password \
    --admin-username cursist1 \
    # --admin-password  \
    --os-disk-delete-option Delete \
    --size Standard_D2ds_v5 \
    --nic-delete-option Delete \
    --public-ip-sku Standard \
    --nsg-rule SSH
    # --custom-data cloud-init.txt

# Sidestep
az vm open-port --resource-group KoensSpeelzaal --name airflowcursus-vm4 --port 3389