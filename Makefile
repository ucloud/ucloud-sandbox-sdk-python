.PHONY: setup lint format test

setup:
	poetry install

lint:
	ruff check .

format:
	ruff format .

test: setup
	poetry run pytest --verbose --numprocesses=4
