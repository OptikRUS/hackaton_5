.PHONY: black-check
black-check:
	black --check .

.PHONY: lint
lint:
	poetry run ruff check src

.PHONY: fix
fix:
	poetry run ruff check --fix src && black .

.PHONY: build
build:
	docker-compose up --build -d
