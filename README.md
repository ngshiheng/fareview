<h1 align="center"><strong>Fareview</strong></h1>

<p align="center">
  <img width="auto" height="auto" src="https://media.giphy.com/media/3o6MbtelsDZdsbFB7i/giphy.gif">
</p>
<br />

[![CI](https://github.com/ngshiheng/fareview/actions/workflows/ci.yml/badge.svg)](https://github.com/ngshiheng/fareview/actions/workflows/ci.yml)
[![CD](https://github.com/ngshiheng/fareview/actions/workflows/cd.yml/badge.svg)](https://github.com/ngshiheng/fareview/actions/workflows/cd.yml)
[![Generate CSV](https://github.com/ngshiheng/fareview/actions/workflows/generate_csv.yml/badge.svg)](https://github.com/ngshiheng/fareview/actions/workflows/generate_csv.yml)

## What is Fareview?

✔️ A simple & easy to use e-commerce price monitoring tool for vendors.

🖥 Monitor product prices on top e-commerce platforms in Singapore.

📈 Increase your sales and profit margins by uncovering your competitors' prices.

## Table of Content

- [What is Fareview?](#what-is-fareview)
- [Table of Content](#table-of-content)
- [Disclaimer](#disclaimer)
- [Content](#content)
- [Development Setup](#development-setup)
  - [Installation](#installation)
  - [Pre-commit Hooks](#pre-commit-hooks)
  - [Database](#database)
- [Usage](#usage)
  - [Start crawling](#start-crawling)
    - [Run single spider](#run-single-spider)
    - [Run all spiders](#run-all-spiders)
    - [Run all spiders, in parallel](#run-all-spiders-in-parallel)
  - [Proxy & Sentry (optional)](#proxy--sentry-optional)
  - [Telegram bot (optional)](#telegram-bot-optional)
- [Contributing](#contributing)

## Disclaimer

This software is only used for research purposes, users must abide by the relevant laws and regulations of their location, please do not use it for illegal purposes. The user shall bear all the consequences caused by illegal use.

## Content

-   You may find the list of commercial beer prices under [`data/`](./data/) or on [this Google Sheets](https://s.jerrynsh.com/fareview)
-   The prices are updated **once daily** using [GitHub action](./.github/workflows/generate_csv.yml)

## Development Setup

### Installation

Make sure you have [poetry](https://python-poetry.org/docs/#installation) installed on your machine.

```sh
poetry install

# Installing dependencies only
poetry install --no-root

# Updating dependencies to their latest versions
poetry update
```

### Pre-commit Hooks

Before you begin your development work, make sure you have installed [pre-commit hooks](https://pre-commit.com/index.html#installation).

Some example useful invocations:

-   `pre-commit install`: Default invocation. Installs the pre-commit script alongside any existing git hooks.
-   `pre-commit install --install-hooks --overwrite`: Idempotently replaces existing git hook scripts with pre-commit, and also installs hook environments.

### Database

-   Make sure you have a running instance of the latest PostgreSQL in your local machine.

```sh
# Example to spin up a PostgreSQL Docker instance locally
docker run -d --name dpostgres -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:latest
```

-   By default, the database for this project should be named as `fareview`.
-   For database migration steps, please read [this](alembic/README.md).

## Usage

### Start crawling

#### Run single spider

```sh
# To list all spiders
poetry run scrapy crawl list

# To run a single spider
poetry run scrapy crawl shopee

# To run single spider with json output
poetry run scrapy crawl shopee -o shopee.json
```

#### Run all spiders

```sh
poetry run scrapy list | xargs -n 1 poetry run scrapy crawl

# Run on Heroku
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

#### Run all spiders, in parallel

```sh
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

### Proxy & Sentry (optional)

[ScraperAPI](https://www.scraperapi.com/?fp_ref=jerryng) is used as our proxy server provider. [Sentry](https://sentry.io/) is used for error monitoring.

```sh
export SCRAPER_API_KEY="<YOUR_SCRAPER_API_KEY>"
export SENTRY_DSN="<YOUR_SENTRY_DSN>"
```

### Telegram bot (optional)

```sh
# Start ngrok
ngrok http 8443

# Change your webhook_url to `https://f4a7bcaf1c23.ngrok.io`, then start app.py
poetry run python3 app.py
```

Click [here](https://t.me/FareviewBot) to sign up for alerts on Telegram.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

1. Fork this
2. Create your feature branch (`git checkout -b feature/bar`)
3. Please make sure you have installed the `pre-commit` hook and make sure it passes all the lint and format check
4. Commit your changes (`git commit -am 'feat: add some bar'`, make sure that your commits are [semantic](https://www.conventionalcommits.org/en/v1.0.0/#summary))
5. Push to the branch (`git push origin feature/bar`)
6. Create a new Pull Request
