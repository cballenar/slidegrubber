#!/usr/bin/env bash
apt-get update
apt-get install -y python-dev python-pip imagemagick
pip install virtualenv

# setup virtual environment
cd /vagrant/
virtualenv venv

# install slidegrubber
python setup.py install