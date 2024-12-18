#!/bin/bash

set -e

cd /app

pip3 install -r requirements.txt
cp /tmp/user.svg /app/assets/avatars/

python3 manage.py makemigrations
python3 manage.py migrate
exec $@