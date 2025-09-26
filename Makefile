.PHONY: all clean test

clean-app-logs:
	@echo "Removing general log file 🧹"
	rm general.log

lint:
	@echo "Running linters... 🔍"
	@poetry run ruff check

lint-fix:
	@echo "Fixing lint issues... ✏️"
	@poetry run ruff check --fix

pre-commit-test:
	@echo "Testing pre-commit hooks... 📡"
	poetry run pre-commit run --all-files

dep-start:
	@echo "Starting containers... 🆙"
	@docker compose up -d

dep-stop:
	@echo "Stopping containers... ⏱️"
	@docker compose stop

dep-down: 
	@echo "Removing containers... 💀"
	@docker compose down

run: dep-start
	@echo "Running application... 🏆"
	poetry run python playground/manage.py runserver

celery: dep-start
	@echo "Running Celery Worker and Beat... 🚴⏱️"
	PYTHONPATH=playground celery -A playground worker --loglevel=info & \
	PYTHONPATH=playground celery -A playground beat --loglevel=info

shell:
	poetry run python playground/manage.py shell

create-migrations:
	poetry run python playground/manage.py makemigrations

migrate:
	poetry run python playground/manage.py migrate

test:
	@echo "Running tests... 🧪"
	@echo "Database container must be running... 🆙"
	PYTHONPATH=playground poetry run pytest --cov=playground --cov-report=term-missing -v $(t)