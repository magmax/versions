#!/bin/bash


cd /opt/app
pip install -r /opt/requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:80
