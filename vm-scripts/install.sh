#!/bin/bash

# Install any required packages or dependencies here
sudo apt install python3-pip # to run python -m commands

# Install Chrome dependencies
sudo apt-get install -y wget gnupg2 apt-transport-https ca-certificates software-properties-common && sudo rm -rf /var/lib/apt/lists/*
alias python=python3
echo "alias python=python3" >> ~/.bashrc
# Temporary fix due for this bug, https://stackoverflow.com/questions/79196464/react-js-failed-to-compile-unexpected-end-of-json-input-error, in next 1 year, on new node version release, remove this code 
sudo npm install -g n
sudo n 22.14.0
hash -r 