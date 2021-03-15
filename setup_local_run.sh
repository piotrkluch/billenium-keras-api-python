#!/bin/sh

python3 -m pip install --upgrade pip virtualenv setuptools wheel

python3 -m virtualenv env
source env/bin/activate
pip3 install --upgrade --no-cache-dir -r requirements.txt