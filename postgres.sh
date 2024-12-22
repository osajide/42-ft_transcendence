#!/bin/sh

set -e # exit in first error encountered

psql -U postgres -c "CREATE DATABASE $DB_NAME;"
psql -U postgres -c "
	CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
	GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

