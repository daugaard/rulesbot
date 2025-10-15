[![Test](https://github.com/daugaard/rulesbot/actions/workflows/test.yml/badge.svg)](https://github.com/daugaard/rulesbot/actions/workflows/test.yml)

# RulesBot
AI powered boardgame rules bot.


## Development
### Setup

```
poetry install

poetry shell # start a shell so you don't have to poetry run everything (optional)

python manage.py migrate
python manage.py createsuperuser
```

### Run

```
poetry run python manage.py runserver
```

### Shell

```
poetry run python manage.py shell
```

### Tests

```
poetry run coverage run --source='.' manage.py test
poetry run coverage report
```

## Production
All production deployment and resource management is done with Kamal.

Deploy a new version:
```
kamal deploy
```

### Run a production shell

Login to the server and start a docker container with a shell command:
```
kamal shell
```

To start a django shell:
```
kamal console
```

### Database backup
Databases are backed up daily to an S3 bucket, and retained for 30 days.

You can also create a manual backup with:
```
kamal accessory exec db_backup "sh backup.sh"
```

You can restore the latest backup with:
```
kamal accessory exec db_backup "sh restore.sh"
```
Or a specific backup file:
```
kamal accessory exec db_backup "sh restore.sh <backup-timestamp>"
```


### Cleanup empty chats

```
from chat.models import ChatSession
empty_sessions = ChatSession.no_user_no_messages()
for session in empty_sessions:
  session.delete()
```
