import logging
import os

import scrapy
from fareview.items import FareviewItem
from fareview.utils.scraperapi import get_proxy_url
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class LazadaSpider(scrapy.Spider):
    """
    Filtered by:
    - Beer
    - Rating >= 4
    - Sorted by best match and brand

    It seems to be inevitable that Lazada API tends to return duplicated products
    When duplicated products have different review_count (review_count could be updated in between requests), our pipelines treat it as 2 unique products, which is not right
    This issue was solved using `_unique_id` in pipelines.py

    E.g.: https://www.lazada.sg/products/asahi-dry-beer-can-350ml-pack-of-6-i301158171-s527196221.html?search=1
    """
    name = 'lazada'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': os.environ.get('LAZADA_DOWNLOAD_DELAY', 60),
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'fareview.middlewares.DelayedRequestsMiddleware': 100,
        },
    }

    start_urls = [
        get_proxy_url(f'https://www.lazada.sg/shop-beer/{keyword}/?ajax=true&rating=4')
        for keyword in settings.get('SUPPORTED_BRANDS')
    ] + [
        get_proxy_url(f'https://www.lazada.sg/shop-beer/{keyword}/?ajax=true&page=2&rating=4')
        for keyword in settings.get('SUPPORTED_BRANDS')
    ]

    def parse(self, response):
        logger.info(response.request.headers)
        logger.info(response.ip_address)

        data = response.json()

        if 'rgv587_flag' in data:
            error = f'Rate limited by Lazada. URL <{response.request.url}>. IP <{response.ip_address}>.'

            retry_request = get_retry_request(response.request, reason=error, spider=self)
            if retry_request:
                yield retry_request
            return

        products = data['mods']['listItems']

        # Stop sending requests when the REST API returns an empty array
        if products:
            for product in products:
                loader = ItemLoader(item=FareviewItem(), selector=product)

                review_count = product['review']
                if int(review_count) < 5:
                    continue

                item_id = product['itemId']
                shop_id = product['sellerId']

                attributes = dict(
                    item_id=item_id,
                    shop_id=shop_id,
                    sku_id=product.get('skuId'),
                    discount=product.get('discount'),
                    in_stock=product.get('inStock'),
                    item_rating=product.get('ratingScore'),
                    shop_location=product.get('location'),
                )

                loader.add_value('platform', self.name)

                loader.add_value('name', product['name'])
                loader.add_value('brand', product['brandName'].lower())
                loader.add_value('vendor', product['sellerName'])
                loader.add_value('url', f'https://www.lazada.sg/products/-i{item_id}-s{shop_id}.html')  # We could also use `productUrl` here

                loader.add_value('quantity', product['name'])
                loader.add_value('volume', product['name'])
                loader.add_value('review_count', review_count)
                loader.add_value('attributes', attributes)

                loader.add_value('price', product['price'])
                yield loader.load_item()
