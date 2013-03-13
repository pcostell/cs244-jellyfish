#!/bin/sh

# python setuptools must be installed to run. This can be installed as:
# sudo apt-get install -y python-setuptools
cd ripl && python setup.py install
cd ../
cd riplpox && python setup.py install
cd ../
cd jellyfish && python setup.py install
