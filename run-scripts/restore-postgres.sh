#!/bin/bash
# Use docker exec to pg_restore the database
# Example invocation: ./restore-postgres.sh rulesbot_prod_2021-03-21_16:00:00.sql

# Check for the correct number of arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: ./restore-postgres.sh <backup file>"
    exit 1
fi

# Check that the backup file exists
if [ ! -f "$1" ]; then
    echo "Error: $1 does not exist"
    exit 1
fi

# Copy the backup file to the postgres container
docker cp $1 rulesbot-postgres-prod:/tmp/backup-to-restore

# Restore the database using no-acl and no-owner
docker exec rulesbot-postgres-prod psql -U postgres < /tmp/backup-to-restore.sql
