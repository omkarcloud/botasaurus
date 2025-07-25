#!/bin/bash

sudo apt-get update
# Install required packages and dependencies
sudo apt install -y apache2 python3-pip

python3 -m pip install --break-system-packages --upgrade bota

echo "alias python=python3" >> ~/.bashrc
alias python=python3
