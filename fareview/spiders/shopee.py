import logging
import os
import re

import scrapy
from fareview.items import FareviewItem
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

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
        f'https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=14260&keyword={keyword}&limit=50&match_id=14255&newest=0&order=desc&page_type=search&rating_filter=4&scenario=PAGE_SUB_CATEGORY_SEARCH&skip_autocorrect=1&version=2'
        for keyword in settings.get('SUPPORTED_BRANDS')
    ]

    def parse(self, response):
        logger.info(response.request.headers)

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
                    sold=product.get('sold'),
                    historical_sold=product.get('historical_sold'),
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
                loader.add_value('review_count', review_count)
                loader.add_value('attributes', attributes)

                loader.add_value('price', str(product['price'] / 100000))  # E.g.: '4349000' = '$43.49'
                yield loader.load_item()
