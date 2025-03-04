#!/bin/bash

set -e

cd /app

pip3 install -r requirements.txt
cp /tmp/user.svg /app/assets/avatars/

python3 manage.py makemigrations
python3 manage.py migrate

# if [ -z "$(ls -A "$STATIC_ROOT" 2>/dev/null)" ]; then # -z option is for checking zero-length result
    python manage.py collectstatic --noinput
# else
    # echo "static files already collected"
# fi

exec "$@"