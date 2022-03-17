## Alembic

We use [alembic](https://alembic.sqlalchemy.org/en/latest/) to manage our database migrations for Fareview.

## Steps to generate migration

1. `alembic revision --autogenerate -m "A concise commit message."`
2. Check the auto-generated migration file to see if it makes any sense
3. Once confirm, run `alembic upgrade head` to apply the database migration (Otherwise simply just delete the generated migration file)

_NOTE: You can always use `alembic downgrade -1` to revert any database migrations_

## How to generate migration for an existing database

-   https://stackoverflow.com/a/56651578/10067850
-   Remember to run `alembic stamp head` to tell `sqlalchemy` that the current migration represents the state of the database

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
