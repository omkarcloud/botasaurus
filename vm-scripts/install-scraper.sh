#!/bin/bash

# Check if the repo URL argument is provided
if [ $# -eq 0 ]; then
    echo "Please provide the repo URL as an argument."
    exit 1
fi

# Store the repo URL argument in a variable
repo_url=$1

# Install required packages and dependencies
sudo apt install -y python3-pip
python3 -m pip install bota

# Install the scraper using the provided repo URL
python3 -m bota install-scraper --repo-url "$repo_url"