#!/bin/bash


cd /opt/app
pip install -r /opt/requirements.txt
python manage.py migrate
supervisord -n
