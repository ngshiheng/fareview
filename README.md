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

# References

## Useful Scrapy Tools and Libraries

https://github.com/croqaz/awesome-scrapy

## Useful SQL Queries

To get the price list of all available products

```sql
SELECT
	product_id,
	platform AS "Platform",
	vendor AS "Vendor",
	brand AS "Brand",
	name AS "Product Name",
	review_count AS "No. of Reviews",
	round(price::numeric, 2) AS "Price ($SGD)",
	quantity AS "Quantity (Unit)",
	round((price / quantity)::numeric, 2) AS "Price/Quantity ($SGD)",
	url AS "Product Link",
	TO_CHAR(price.updated_on::TIMESTAMP AT TIME ZONE 'SGT', 'dd/mm/yyyy') AS "Updated On (SGT)"
FROM
	product
	INNER JOIN price ON price.product_id = product.id
ORDER BY
	price / quantity ASC
```

To get the number of prices of all available products

```sql
SELECT
	product.id,
	product.vendor AS "Vendor",
	name AS "Product Name",
	quantity AS "Quantity (Unit)",
	url AS "Product Link",
	count(price.product_id) AS "Number of Prices"
FROM
	product
	LEFT JOIN price ON (product.id = price.product_id)
GROUP BY
	product.id
```

[Dataclip](https://data.heroku.com/dataclips) version 1

```sql
WITH CURRENT_PRICE (
	product_id,
	price
) AS (
	SELECT
		product_id,
		price
	FROM (
		SELECT
			product_id,
			price,
			ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price.updated_on DESC) AS rownum
		FROM
			price) t
	WHERE
		rownum = 1
),
PREVIOUS_PRICE (product_id,
price
) AS (
SELECT
	product_id,
	price
FROM (
SELECT
	product_id,
	price,
	ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price.updated_on DESC) AS rownum
FROM
	price) t
WHERE
	rownum = 2
)
SELECT
	p.id, platform AS "Platform", vendor AS "Vendor", name AS "Product Name", curr.price AS "Current ($SGD)", prev.price AS "Previous ($SGD)", CASE WHEN prev.price IS NULL THEN
		0
	ELSE
		round((curr.price - prev.price)::numeric, 2)
	END AS "Change ($SGD)", review_count AS "Reviews", attributes -> 'sold' AS "Sold", attributes -> 'stock' AS "Stock", url AS "Product URL"
FROM
	product p
	LEFT JOIN CURRENT_PRICE curr ON curr.product_id = p.id
	LEFT JOIN PREVIOUS_PRICE prev ON prev.product_id = p.id
		AND(prev.price <> curr.price)
WHERE
	p.quantity = 24
	AND p.brand = 'carlsberg'
ORDER BY
	p.review_count DESC
LIMIT 30
```

Get current and previous price in the same table. [Dataclip](https://data.heroku.com/dataclips) version 2

```sql
WITH CURRENT_PRICE (
	product_id,
	price
) AS (
	SELECT
		product_id,
		price
	FROM (
		SELECT
			product_id,
			price,
			ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price.updated_on DESC) AS rownum
		FROM
			price) t
	WHERE
		rownum = 1
),
PREVIOUS_PRICE (product_id,
price
) AS (
SELECT
	product_id,
	price,
	updated_on
FROM (
SELECT
	product_id,
	price,
	updated_on,
	ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price.updated_on DESC) AS rownum
FROM
	price) t
WHERE
	rownum = 2
)
SELECT
	platform AS "Platform", vendor AS "Vendor", name AS "Product Name", curr.price AS "Current ($SGD)", prev.price AS "Previous ($SGD)", CASE WHEN prev.price IS NULL THEN
		NULL
	ELSE
		round((curr.price - prev.price)::numeric, 2)
	END AS "Change ($SGD)", review_count AS "Reviews", attributes -> 'sold' AS "Sold", attributes -> 'stock' AS "Stock", url AS "Product URL", TO_CHAR(p.updated_on + INTERVAL '8 HOUR', 'DD-MON-YYYY HH24:MM') AS "Last Checked", TO_CHAR(prev.updated_on + INTERVAL '8 HOUR', 'DD-MON-YYYY HH24:MM') AS "Last Change"
FROM
	product p
	LEFT JOIN CURRENT_PRICE curr ON curr.product_id = p.id
	LEFT JOIN PREVIOUS_PRICE prev ON prev.product_id = p.id
		AND(prev.price <> curr.price)
WHERE
	p.quantity = 24
	AND p.brand = 'carlsberg'
ORDER BY
	p.review_count DESC
LIMIT 30
```
