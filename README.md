# Django Playground

Repository to build and practice Python, Django and a lot of other stuffs :hammer:

## :bulb: Techs

- Python
- Poetry
- Django and Django REST Framework
- PostgreSQL
- Docker and Docker Compose

## :running: Running locally

#### Installing Python

Using `pyenv`:

```bash
pyenv install 3.12

pyenv virtualenv 3.12 django-playground

pyenv activate django-playground
```

#### Handling containers and environment

Copy `.env` file

```
cp .env.example .env
```

To start all containers:

```
make dep-start
```

To stop all containers:

```
make dep-stop
```

To remove all containers:

```
make dep-down
```

#### Installing dependencies

[Poetry must be installed](https://python-poetry.org/docs/#installation). To install all projects dependencies defined at `pyproject.toml`:

```
poetry install --no-root
```

#### Running applications

To run APIs on port `8000`:

```
make run
```

After running you can validate if it's ok call `ping`:

```
curl --location 'http://localhost:8000/ping/'
```

#### Applying migrations

To apply all migrations:

```
make migrations
```

#### Linting

The playground uses `ruff` and `pre-commit` with different hooks. To check:

```
make lint
```

Applying lint fixes:

```
make lint-fix
```

The `pre-commit` hooks fixes automatically and to test manually:

```
make pre-commit-test
```

**Note:** There are pre-commit hooks defined for README files, `Makefile` and other config files, commit messages and `ruff` itself. [It was based on this Medium article](https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835)

## :open_file_folder: Applications

The goal of `django-playground` is to represent multiple applications and practices to learn about stuff and it also represents that monolithic application that everybody knows which does everything and have multiple contexts.

### :moneybag: Payments

The Payments application is at `playground/payments`.

For more details take a look at [payments docs](./playground/payments/README.md)

______________________________________________________________________

Made with :heart: for studies by [RafaelEmery](https://github.com/RafaelEmery)
