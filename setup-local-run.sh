#!/bin/sh

python -m pip install --upgrade pip virtualenv setuptools wheel

python -m virtualenv env
source env/bin/activate
pip install --upgrade --no-cache-dir -r requirements.txt