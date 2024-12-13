#!/bin/sh

set -e # exit in first error encountered

psql -U postgres -c "CREATE DATABASE django_database;"
psql -U postgres -c "
	CREATE USER django_user WITH PASSWORD '1234';
	GRANT ALL PRIVILEGES ON DATABASE django_database TO django_user;"

