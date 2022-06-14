install:
	poetry install --no-root

lint:
	poetry run flake8 --statistics --show-source

pre-commit:
	poetry run pre-commit run
