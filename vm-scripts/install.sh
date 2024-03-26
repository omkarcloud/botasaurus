#!/bin/bash

# Install any required packages or dependencies here
sudo apt install python3-pip # to run python -m commands

# Install Chrome dependencies
sudo apt-get install -y wget gnupg2 apt-transport-https ca-certificates software-properties-common && sudo rm -rf /var/lib/apt/lists/*
