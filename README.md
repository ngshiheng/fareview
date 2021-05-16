# Fareview

Simple, fast market price scanner

<script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/2578_RC01/embed_loader.js"></script> <script type="text/javascript"> trends.embed.renderExploreWidget("TIMESERIES", {"comparisonItem":[{"keyword":"Tiger","geo":"SG","time":"today 12-m"},{"keyword":"Heineken","geo":"SG","time":"today 12-m"},{"keyword":"Carlsberg","geo":"SG","time":"today 12-m"},{"keyword":"Guinness","geo":"SG","time":"today 12-m"},{"keyword":"Asahi","geo":"SG","time":"today 12-m"}],"category":404,"property":""}, {"exploreQuery":"cat=404&geo=SG&q=Tiger,Heineken,Carlsberg,Guinness,Asahi&date=today 12-m,today 12-m,today 12-m,today 12-m,today 12-m","guestPath":"https://trends.google.com:443/trends/embed/"}); </script>

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
