#!/usr/bin/env bash

sudo apt update
sudo apt install -y tmux vim zsh supervisor
#intall oh my zsell
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

#wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
#chmod +x Berryconda3-2.0.0-Linux-armv7l.sh
#./Berryconda3-2.0.0-Linux-armv7l.sh

sudo apt install -y dirmngr
sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 2C0D3C0F
sudo wget http://goo.gl/vewCLL -O /etc/apt/sources.list.d/rpimonitor.list
sudo apt update
sudo apt install -y rpimonitor
sudo /etc/init.d/rpimonitor update



supo apt install -y python3-ipython
sudo apt install -y  python3-rpi.gpio
sudo apt install -y python3-dev
sudo apt install -y python3-pandas

sudo pip3 install --upgrade pip
sudo pip3 install pi-sht1x
sudo pip3 install jupyter
sudo pip3 install jupyterlab
sudo jupyter notebook --generate-config
sudo awk '/#c.NotebookApp.ip/ { gsub(/localhost/, "*") }; { print }' /root/.jupyter/jupyter_notebook_config.py > /tmp/jc.py
sudo mv /tmp/jc.py /root/.jupyter/jupyter_notebook_config.py
sudo awk '/#c.NotebookApp.ip/ { gsub(/#c.NotebookApp/, "c.NotebookApp") }; { print }' /root/.jupyter/jupyter_notebook_config.py > /tmp/jc.py
sudo mv /tmp/jc.py /root/.jupyter/jupyter_notebook_config.py

sudo jupyter notebook password

#sudo jupyter lab --allow-root --notebook-dir=./

sudo git clone https://github.com/daliagachc/pi-vertical-garden.git
git config --global user.email "daliaga@chacaltaya.edu.bo"
git config --global user.name "daliagachc"
sudo git config --global user.email "daliaga@chacaltaya.edu.bo"
sudo git config --global user.name "daliagachc"
sudo pip3 install -e ./pi-vertical-garden/
