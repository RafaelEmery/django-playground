.PHONY: all clean test

lint:
	@echo "Running linters... 🔍"
	@poetry run ruff check

lint-fix:
	@echo "Fixing lint issues... ✏️"
	@poetry run ruff check --fix

pre-commit-test:
	@echo "Testing pre-commit hooks... 📡"
	poetry run pre-commit run --all-files

clean-app-logs:
	@echo "Removing general log file 🧹"
	rm general.log

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

shell:
	poetry run python playground/manage.py shell

create-migrations:
	poetry run python playground/manage.py makemigrations

migrate:
	poetry run python playground/manage.py migrate

test:
	@echo "Running tests... 🧪"
	@echo "Database container must be running... 🆙"
	PYTHONPATH=playground poetry run pytest --cov=playground --cov-report=term-missing -v