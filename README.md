# Fareview

Simple, fast market price scanner

## Useful SQL Queries

To get the price list of all available products

```sql
SELECT
	product_id,
	platform AS "Platform",
	vendor AS "Vendor",
	name AS "Product Name",
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
