[![Test](https://github.com/daugaard/rulesbot/actions/workflows/test.yml/badge.svg)](https://github.com/daugaard/rulesbot/actions/workflows/test.yml)

# RulesBot
AI powered boardgame rules bot.

## Setup

```
poetry install

poetry shell # start a shell so you don't have to poetry run everything

python manage.py migrate
python manage.py createsuperuser
```

## Run

```
python manage.py runserver
```

## Shell

```
python manage.py shell
```

## Tests

```
coverage run --source='.' manage.py test
coverage report
```

## Deploy

First build:
```
docker build . -t rulesbot -t registry.practicalai.io/rulesbot && docker push registry.practicalai.io/rulesbot
```

Then login to server and reload rulesbot container:
```
./apps/run-rulesbot-container.sh
```
