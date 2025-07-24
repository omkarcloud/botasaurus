#!/bin/bash

sudo apt-get update
sudo apt install apache2
# Install required packages and dependencies
sudo apt install -y python3-pip # see rm works
python3 -m pip install --break-system-packages --upgrade bota
alias python=python3
echo "alias python=python3" >> ~/.bashrc

alias python=python3
