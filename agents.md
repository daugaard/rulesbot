# AGENTS.md

## Setup commands
- Install deps: `poetry install`
- Start dev server: `poetry run python manage.py runserver`
- Run tests: `poetry run manage.py test`
- Run tests with coverage: `poetry run coverage run --source='.' manage.py test` then `coverage report`

## Code style
- Use `black` for code formatting: `poetry run black .`
- Use `flake8` for linting: `poetry run flake8 .`
- Use `isort` for import sorting: `poetry run isort .`

## General Guidelines
- Follow PEP 8 style guidelines.
- Write clear, concise, and well-documented code.
- Ensure all new features have corresponding tests.
- Always use Django best practices for models, views, and templates.
