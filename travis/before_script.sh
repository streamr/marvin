#!/bin/sh

# Set up the SSH key
echo -n $id_rsa_{00..43} >> ~/.ssh/id_rsa_base64
base64 --decode --ignore-garbage ~/.ssh/id_rsa_base64 > ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa

# Configure git
git remote set-url origin $REPO.git
git config --global user.email "tarjei@roms.no"
git config --global user.name "Tarjei Husøy (via Travis CI)"
