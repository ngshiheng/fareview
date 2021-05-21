<h1 align="center"><strong>Fareview</strong></h1>

<p align="center">
  <img width="auto" height="auto" src="https://media.giphy.com/media/3o6MbtelsDZdsbFB7i/giphy.gif">
</p>
<br />

# What is Fareview?

✔️ A simple & easy to use e-commerce price monitoring tool for vendors.

🖥 Monitor product prices on top e-commerce platforms in Singapore.

📈 Increase your sales and profit margins by uncovering your competitors' prices.

# Project Usage Guide

## Start Crawling

### Run single spider

```sh
# To list all spiders
pipenv run scrapy crawl list

# To run a single spider
pipenv run scrapy crawl shopee

# To run single spider with json output
pipenv run scrapy crawl shopee -o shopee.json
```

### Run all spiders

```sh
pipenv run scrapy list | xargs -n 1 pipenv run scrapy crawl

# Run on Heroku
heroku run scrapy list | xargs -n 1 heroku run scrapy crawl
```

### Run all spiders, in parallel

```sh
scrapy list | xargs -n 1 -P 0 scrapy crawl
```

## Using Proxy (For Production)

```sh
export SCRAPER_API_KEY="YOUR_SCRAPER_API_KEY"
```

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
