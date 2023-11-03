#!/bin/bash

# Use docker exec to pg_dump the database
docker exec -it rulesbot-postgres-prod pg_dump -U postgres -d rulesbot > rulesbot_prod.sql

# Copy the dump to the db back up folder with current timestamp
cp rulesbot_prod.sql ~/apps/db-backups/rulesbot_prod_$(date +%Y-%m-%d_%H-%M-%S).sql

# Remove the dump
rm rulesbot_prod.sql
