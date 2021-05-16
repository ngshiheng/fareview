<h1 align="center"><strong>Fareview</strong></h1>

<p align="center">
  <img width="auto" height="auto" src="https://media.giphy.com/media/3o6MbtelsDZdsbFB7i/giphy.gif">
</p>
<br />

<script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/2578_RC01/embed_loader.js"></script> <script type="text/javascript"> trends.embed.renderExploreWidget("TIMESERIES", {"comparisonItem":[{"keyword":"Tiger","geo":"SG","time":"today 12-m"},{"keyword":"Heineken","geo":"SG","time":"today 12-m"},{"keyword":"Carlsberg","geo":"SG","time":"today 12-m"},{"keyword":"Guinness","geo":"SG","time":"today 12-m"},{"keyword":"Asahi","geo":"SG","time":"today 12-m"}],"category":404,"property":""}, {"exploreQuery":"cat=404&geo=SG&q=Tiger,Heineken,Carlsberg,Guinness,Asahi&date=today 12-m,today 12-m,today 12-m,today 12-m,today 12-m","guestPath":"https://trends.google.com:443/trends/embed/"}); </script>

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
