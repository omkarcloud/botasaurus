#!/bin/bash

sudo apt-get update
# Install required packages and dependencies
sudo apt install -y python3-pip
python3 -m pip install bota
alias python=python3