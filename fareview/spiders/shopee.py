import logging
import os
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

from fareview.items import FareviewItem

logger = logging.getLogger(__name__)

settings = get_project_settings()


class ShopeeSpider(scrapy.Spider):
    """
    Filtered by:
    - Beer & Cider
    - Rating >= 4
    - Sorted by top sales

    There's a unique scenario where by a single shop/vendor (within the same url) are selling multiple products
    Because of this, our database model unique constraint with just quantity & url won't work anymore
    In this scenario, we made the change to our database model unique index to be brand + quantity + url
    See `_unique_id` in pipelines.py
    """
    name = 'shopee'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('SHOPEE_DOWNLOAD_DELAY', 5),
    }

    start_urls = [
        f'https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword={keyword}&limit=60&newest=0&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2'
        for keyword in settings.get('SUPPORTED_BRANDS')
    ]

    headers = {
        'af-ac-enc-dat': 'AAcyLjQuMS0yAAABhEL7l5QAAAtFAj4AAAAAAAAAAOYyhFAbVQMMpIKa2+dGIBkKaWUVkWOzjLDykZY2dhCO2aemln1UTUS5+au1jIfY7R1Euk28HZ2GTC6Gy8upKta1AomlahQQzJTI3QAyabrcR+HjRE5RJ4xmgqF0pQNNgJWI5Ixc+XXsPExyZcR6n6fQ8y9qv9e+0i2RFxL9D/LW5RfDxbm3aN4QLhF3xSQUSdhFgxFdjSR7fl8kZiNFp11d12JqI4GTqcIATPt0rYY/lg4GZtDRXf4x2yTcLYISZjjnR9AUjPhml6U83c4YR74/vnZjSA2ERGYorMHDENw4Z9+Tuci8nLq+lJGsF/QQZ4cpeG2ZUbatRPTf42k24UXHBZsicXs8yj3KGje9gM5DBdGp9SC7AzprcJ/dvAMt1ZE2pQeZodbQEboXldfnVQFaMWIRa4PXPgZbPTbQrS6pIpLnj37lZQEr3GBZds8j2v70yZKvj0zWrczR/hh97tTxzycK0Dv39rAuuGC+V6bDol7tQtal5Gv4mni39rtOgLdZw4Hfjpcb9HHvBsWrWyhnyF1hqOdk2mvItkQwyQJac9YQx1Jd3lC+REE4Rd+g0DJE9KlDf2xEAkaDTZA0clzBUpm1uAhv9Tyih0QRRViyudt/vxC3q7r7Amu/FcS/fiwQIrKIho5LxORIkIvYHmXWjcsYEz9S9S9p+tV1HIfZaPBju6lh2dK2YKJ14RudySmaqnWRY7OMsPKRljZ2EI7Zp6aWkWOzjLDykZY2dhCO2aemlszDf5SsFtL4FgoZmajdOR0=',
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        """
        @url https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword=carlsberg&limit=60&newest=0&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2
        @returns items 1
        @returns requests 0 0
        @scrapes platform name brand vendor url quantity review_count attributes price
        """
        logger.info(response.request.headers)
        logger.info(response.ip_address)

        data = response.json()
        items = data['items']

        brand = re.search(r'keyword=(\w+)&', response.request.url).group(1)

        # Stop sending requests when the REST API returns an empty array
        if items:
            for item in items:
                product = item['item_basic']

                loader = ItemLoader(item=FareviewItem())

                review_count = product['item_rating']['rating_count'][0]
                if review_count < 20:
                    continue

                item_id = str(product['itemid'])
                shop_id = str(product['shopid'])

                attributes = dict(
                    item_id=item_id,
                    shop_id=shop_id,
                    discount=product.get('discount'),
                    stock=product.get('stock'),
                    sold=product.get('historical_sold'),
                    liked_count=product.get('liked_count'),
                    view_count=product.get('view_count'),
                    item_rating=product.get('item_rating'),
                    shop_location=product.get('shop_location'),
                )

                loader.add_value('platform', self.name)

                loader.add_value('name', product['name'])
                loader.add_value('brand', brand)  # NOTE: Shopee's API product['brand'] does not guarantee that brand is always correct
                loader.add_value('vendor', shop_id)
                loader.add_value('url', f'https://shopee.sg/--i.{shop_id}.{item_id}')

                loader.add_value('quantity', product['name'])
                loader.add_value('volume', product['name'])
                loader.add_value('review_count', review_count)
                loader.add_value('attributes', attributes)

                loader.add_value('price', str(product['price'] / 100000))  # E.g.: '4349000' = '$43.49'
                yield loader.load_item()
