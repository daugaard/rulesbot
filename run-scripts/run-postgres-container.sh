docker run -d --name rulesbot-postgres-prod --restart unless-stopped --net rulesbot-prod --env-file .postgres-env -v ~/apps/volumes/rulesbot-prod-postgres:/var/lib/postgresql/data postgres:alpine
