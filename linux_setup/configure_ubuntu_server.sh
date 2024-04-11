#!/bin/bash

set -e

# Add docker repo
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Add vs-code repo
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg

# Add pgadmin repo
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" | sudo tee /etc/apt/sources.list.d/pgadmin4.list > /dev/null

# Install all packages
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y wget gpg curl gnupg lsb-release xrdp gh apt-transport-https docker-ce docker-ce-cli containerd.io docker-compose-plugin pgadmin4-desktop code

# Install xfce4 separately
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install xfce4
sudo apt-get install -y xfce4-session

# Install asdf and python
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.11.1
echo -e "\n# asdf initialisation\nif [ -f $HOME/.asdf/asdf.sh ]; then\n    . $HOME/.asdf/asdf.sh\nfi\n\n# asdf completions initialisation\nif [ -f $HOME/.asdf/completions/asdf.bash ]; then\n    . $HOME/.asdf/completions/asdf.bash\nfi" >> ~/.bashrc 
source ~/.bashrc
asdf plugin-add python
asdf install python 3.11.8
asdf global python 3.11.8

# Setup xrdp
sudo systemctl enable xrdp
sudo adduser xrdp ssl-cert
echo xfce4-session >~/.xsession
sudo service xrdp restart

# Install chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt --fix-broken install -y
rm -f google-chrome-stable_current_amd64.deb

# Remove usage of sudo when using docker
sudo usermod -aG docker $USER

# Clone the development setup
gh auth login
gh repo clone DatalabFabriek/dl-air-devsetup /home/$USER/airflow-development
gh auth logout
rm -rf ~/airflow-development/.git