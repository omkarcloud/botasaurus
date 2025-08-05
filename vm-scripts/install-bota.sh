#!/bin/bash

sudo apt-get update
# Install required packages and dependencies
sudo apt install -y apache2 python3-pip
python3 -m pip install --break-system-packages --upgrade bota

echo "alias python=python3" >> ~/.bashrc
# Temporary fix due for this bug, https://stackoverflow.com/questions/79196464/react-js-failed-to-compile-unexpected-end-of-json-input-error, in next 1 year, on new node version release, remove this code 
sudo npm install -g n
sudo n 22.14.0
hash -r 

alias python=python3