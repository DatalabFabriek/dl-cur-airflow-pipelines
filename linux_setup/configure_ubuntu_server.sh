
sudo su

# Add docker repo
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Add vs-code repo
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg

# Add pgadmin repo
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

# Install all packages
apt-get update
apt-get upgrade -y
apt-get install -y wget gpg curl gnupg lsb-release xrdp gh apt-transport-https docker-ce docker-ce-cli containerd.io docker-compose-plugin pgadmin4-desktop

# Install xfce4 seperately
DEBIAN_FRONTEND=noninteractive apt-get -y install xfce4
apt-get install -y xfce4-session

# Install asdf and python
apt install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.11.1
echo "
# asdf initialisation
if [ -f $HOME/.asdf/asdf.sh ]; then
    . $HOME/.asdf/asdf.sh
fi

# asdf completions initialisation
if [ -f $HOME/.asdf/completions/asdf.bash ]; then
    . $HOME/.asdf/completions/asdf.bash
fi" >> /home/cursist1/.bashrc 
bash && asdf plugin-add python
asdf install python 3.10.9
asdf global python 3.10.9

# Setup xrdp
systemctl enable xrdp;
adduser xrdp ssl-cert;
echo xfce4-session >~/.xsession;
service xrdp restart;

# Install chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb
apt --fix-broken install
rm -f google-chrome-stable_current_amd64.deb

# Remove usage of sudo when using docker
usermod -aG docker cursist1

# Change to cursist1 user
su - cursist1

# Pull devsetup
echo '' > my_token.txt
gh auth login --with-token < my_token.txt
gh repo clone DatalabFabriek/dl-air-devsetup /home/cursist1/airflow-development
gh auth logout
rm -rf /home/cursist1/airflow-development/.git
rm -f my_token.txt