#!/bin/bash
set -e

# Create wagtail database
psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE DATABASE wagtail;
    GRANT ALL PRIVILEGES ON DATABASE wagtail TO postgres;
EOSQL

echo "Database initialized successfully!"
