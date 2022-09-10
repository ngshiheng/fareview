NAME := fareview
POETRY := $(shell command -v poetry 2> /dev/null)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Use 'make <target>' where <target> is one of:"
	@echo ""
	@echo "  install	install packages and prepare environment"
	@echo "  clean		remove all temporary files"
	@echo "  lint		run the code linters"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

install:
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install --no-root

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf .scrapy

.PHONY: lint
lint:
	$(POETRY) run flake8 --statistics --ignore=W503,E501 --show-source

build:
	docker build -t fareview . \
	--build-arg PG_HOST=172.17.0.1 \
	--build-arg PG_PORT=5432 \
	--build-arg ENVIRONMENT="development"

run:
	docker stop $(NAME) || true && docker rm $(NAME) || true
	docker run -d --name $(NAME) $(NAME)
