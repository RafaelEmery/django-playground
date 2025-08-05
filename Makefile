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

migrate:
	poetry run python playground/manage.py migrate