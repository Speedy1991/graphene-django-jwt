#!/bin/bash

echo "Migrate"
python manage.py migrate

echo "Clear Tokens"
python manage.py cleartokens --expired

# TODO load fixtures
python manage.py runserver 0.0.0.0:8000
