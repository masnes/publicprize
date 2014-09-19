#!/bin/sh
. ~/.bash_profile
cd ~/publicprize
python manage.py runserver -h localhost -p 8000
