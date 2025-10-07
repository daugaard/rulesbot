[![Test](https://github.com/daugaard/rulesbot/actions/workflows/test.yml/badge.svg)](https://github.com/daugaard/rulesbot/actions/workflows/test.yml)

# RulesBot
AI powered boardgame rules bot.

## Setup

```
poetry install

poetry shell # start a shell so you don't have to poetry run everything (optional)

python manage.py migrate
python manage.py createsuperuser
```

## Run

```
poetry run python manage.py runserver
```

## Shell

```
poetry run python manage.py shell
```

## Tests

```
poetry run coverage run --source='.' manage.py test
poetry run coverage report
```

## Deploy

First build:
```
docker build . -t rulesbot -t registry.practicalai.io/rulesbot && docker push registry.practicalai.io/rulesbot
```

Then login to server and reload rulesbot container:
```
cd apps
./run-rulesbot-container.sh
```

### Run a production shell

Login to the server and start a docker container with a shell command:
```
docker run -it --rm --env-file .rulesbot-env --net rulesbot-prod registry.practicalai.io/rulesbot /bin/bash
poetry run ./manage.py shell
```


### Cleanup empty chats

```
from chat.models import ChatSession
empty_sessions = ChatSession.no_user_no_messages()
for session in empty_sessions:
  session.delete()
```
