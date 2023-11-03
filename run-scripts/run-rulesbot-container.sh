#!/bin/bash

# This script is used to run the rulesbot container in production mode.
docker pull registry.practicalai.io/rulesbot:latest
docker stop rulesbot-prod
docker rm rulesbot-prod
docker run -d --restart unless-stopped --name rulesbot-prod --net rulesbot-prod -p 5000:5000 --env-file .rulesbot-env registry.practicalai.io/rulesbot:latest

# Collect static files
docker exec -it rulesbot-prod poetry run python manage.py collectstatic --noinput

# Migrate the database
docker exec -it rulesbot-prod poetry run python manage.py migrate

# Finally restart to serve static files properly after they have been collected
docker restart rulesbot-prod
