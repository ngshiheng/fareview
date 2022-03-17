[![CI](https://github.com/ngshiheng/fareview/actions/workflows/ci.yml/badge.svg)](https://github.com/ngshiheng/fareview/actions/workflows/ci.yml)
[![Semantic Release](https://github.com/ngshiheng/fareview/actions/workflows/release.yml/badge.svg)](https://github.com/ngshiheng/fareview/actions/workflows/release.yml)

<h1 align="center"><strong>Fareview</strong></h1>

<p align="center">
  <img width="auto" height="auto" src="https://media.giphy.com/media/3o6MbtelsDZdsbFB7i/giphy.gif">
</p>
<br />

# What is Fareview?

✔️ A simple & easy to use e-commerce price monitoring tool for vendors.

🖥 Monitor product prices on top e-commerce platforms in Singapore.

📈 Increase your sales and profit margins by uncovering your competitors' prices.

## Demo

-   You may find the list of commercial beer prices [here](https://docs.google.com/spreadsheets/d/1ImvPhsWp3mRF5lz7C55Ub2Z5okzitIvU6WG77YWL5PU/edit?usp=sharing)
-   Prices updated **once** daily
-   Click [here](https://t.me/FareviewBot) to sign up for alerts

# Development Setup

## Installation

Make sure you have [poetry](https://python-poetry.org/docs/#installation) installed on your machine.

```sh
poetry install

# Installing dependencies only
poetry install --no-root

# Updating dependencies to their latest versions
poetry update
```

## Pre-commit Hooks

Before you begin your development work, make sure you have installed [pre-commit hooks](https://pre-commit.com/index.html#installation).

Some example useful invocations:

-   `pre-commit install`: Default invocation. Installs the pre-commit script alongside any existing git hooks.
-   `pre-commit install --install-hooks --overwrite`: Idempotently replaces existing git hook scripts with pre-commit, and also installs hook environments.

## Database

-   Make sure you have a running instance of the latest PostgreSQL in your local machine.

```sh
# Example to spin up a PostgreSQL Docker instance locally
docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest
```

-   By default, the database for this project should be named as `fareview`.
-   For database migration steps, please read [this](alembic/README.md).

# Usage

## Start Crawling

### Run single spider

```sh
# To list all spiders
poetry run scrapy crawl list

# To run a single spider
poetry run scrapy crawl shopee

# To run single spider with json output
poetry run scrapy crawl shopee -o shopee.json
```

### Run all spiders

```sh
poetry run scrapy list | xargs -n 1 poetry run scrapy crawl

# Run on Heroku
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

### Run all spiders, in parallel

```sh
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

## Optional: Using Proxy (For Production)

```sh
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
```

## Telegram Bot

```sh
# Start ngrok
ngrok http 8443

# Change your webhook_url to `https://f4a7bcaf1c23.ngrok.io`, then start app.py
poetry run python3 app.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Steps

1. Fork this
2. Create your feature branch (`git checkout -b feature/bar`)
3. Please make sure you have installed the `pre-commit` hook and make sure it passes all the lint and format check
4. Commit your changes (`git commit -am 'feat: add some bar'`, make sure that your commits are [semantic](https://www.conventionalcommits.org/en/v1.0.0/#summary))
5. Push to the branch (`git push origin feature/bar`)
6. Create a new Pull Request

# References

## Useful Scrapy Tools and Libraries

-   https://github.com/croqaz/awesome-scrapy
