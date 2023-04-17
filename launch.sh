#!/bin/bash

echo ***Installing dependencies
python3 -m pip install --upgrade pip
pip3 install requests
pip3 install mininet
sudo python3 run.py
sudo mn -c
python3 ship-logs.py
