import logging
import os
import re

import scrapy
from fareview.items import FareviewItem
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class RedMartSpider(scrapy.Spider):
    """
    Whenever HTTPCACHE_ENABLED is True, retry requests doesn't seem to work well
    I have a feeling that is because referer is being set with cached which Lazada endpoints don't seem to like it
    """
    name = 'redmart'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('REDMART_DOWNLOAD_DELAY', 30),
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'fareview.middlewares.DelayedRequestsMiddleware': 100,
        },
        'HTTPCACHE_ENABLED': False,
    }

    start_urls = [
        f'https://redmart.lazada.sg/shop-beer/{keyword}/?ajax=true&m=redmart&rating=4'
        for keyword in settings.get('SUPPORTED_BRANDS')
    ]

    def _get_product_quantity(self, package_info: str) -> int:
        raw_quantity = re.split('×', package_info)  # E.g.: "40 × 320 ml", "330 ml"

        if len(raw_quantity) > 1:
            return int(raw_quantity[0])

        return 1

    def parse(self, response):
        logger.info(response.request.headers)
        logger.info(response.ip_address)

        data = response.json()

        if 'rgv587_flag' in data:
            error = f'Rate limited by Red Mart. URL <{response.request.url}>. IP <{response.ip_address}>.'

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

                loader.add_value('quantity', self._get_product_quantity(product['packageInfo']))
                loader.add_value('review_count', review_count)
                loader.add_value('attributes', attributes)

                loader.add_value('price', product['price'])
                yield loader.load_item()
