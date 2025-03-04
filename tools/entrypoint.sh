#!/bin/sh

# echo hello

# echo pwd
# pwd

# echo cd
cd /conf

# echo ls
# ls
# echo "cat file before"
# cat alertmanager.yml

sed -i "s|\${RECEIVER}|$RECEIVER|" alertmanager.yml
sed -i "s|\${SENDER}|$SENDER|" alertmanager.yml
sed -i "s|\${SMTP_SERVER}|$SMTP_SERVER|" alertmanager.yml
sed -i "s|\${AUTH_USERNAME}|$AUTH_USERNAME|" alertmanager.yml
sed -i "s|\${AUTH_PASSWORD}|$AUTH_PASSWORD|" alertmanager.yml

# echo "cat file after"
# cat alertmanager.yml

# taken from ps command in alertmanager container
exec /bin/alertmanager --config.file=/conf/alertmanager.yml --storage.path=/alertmanager
