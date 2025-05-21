#!/bin/bash

# Check if the repo URL argument is provided
if [ $# -eq 0 ]; then
    echo "Please provide the repo URL as an argument."
    exit 1
fi

# Store the repo URL argument in a variable
repo_url=$1

sudo apt-get update
# Install required packages and dependencies
sudo apt install -y python3-pip
python3 -m pip install --upgrade bota
alias python=python3
echo "alias python=python3" >> ~/.bashrc
# Temporary fix due for this bug, https://stackoverflow.com/questions/79196464/react-js-failed-to-compile-unexpected-end-of-json-input-error, in next 1 year, on new node version release, remove this code 
sudo npm install -g n
sudo n 22.14.0
hash -r 

# Install the scraper using the provided repo URL
python3 -m bota install-ui-scraper --repo-url "$repo_url"