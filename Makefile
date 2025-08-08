lint:
	@echo "Running linters... 🔍"
	@poetry run ruff check

lint-fix:
	@echo "Fixing lint issues... ✏️"
	@poetry run ruff check --fix

dep-start:
	@echo "Starting containers... 🆙"
	@docker compose up -d

dep-stop:
	@echo "Stopping containers... ⏱️"
	@docker compose stop

dep-down: 
	@echo "Removing containers... 💀"
	@docker compose down

run:
	poetry run python playground/manage.py runserver

shell:
	poetry run python playground/manage.py shell

create-migrations:
	poetry run python playground/manage.py makemigrations

migrate:
	poetry run python playground/manage.py migrate