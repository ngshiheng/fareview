import logging
import os

import scrapy
from fareview.items import FareviewItem
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class ShopeeSpider(scrapy.Spider):
    """
    Available Data from Shopee's API:
    stock
    sold
    historical sold
    view_count
    brand
    price

    https://shopee.sg/api/v4/search/search_items?by=sales&keyword=carlsberg&limit=50&newest=50&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2

    Filtered by:
    - Beer & Cider
    - Rating >= 4
    - Sorted by top sales
    """
    name = 'shopee'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('SHOPEE_DOWNLOAD_DELAY', 5),
    }

    start_urls = [
        f'https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=14260&keyword={keyword}&limit=50&match_id=14255&newest=0&order=desc&page_type=search&rating_filter=4&scenario=PAGE_SUB_CATEGORY_SEARCH&skip_autocorrect=1&version=2'
        for keyword in ['tiger', 'Heineken', 'carlsberg', 'guinness', 'asahi']
    ]

    def parse(self, response):
        logger.info(response.request.headers)
        data = response.json()

        items = data['items']

        # Stop sending requests when the REST API returns an empty array
        if items:
            for item in items:
                product = item['item_basic']

                loader = ItemLoader(item=FareviewItem())

                item_id = str(product['itemid'])
                shop_id = str(product['shopid'])

                loader.add_value('platform', self.name)

                loader.add_value('name', product['name'])
                loader.add_value('brand', product['brand'])
                loader.add_value('vendor', shop_id)
                loader.add_value('url', f'https://shopee.sg/--i.{shop_id}.{item_id}')
                loader.add_value('quantity', product['name'])

                loader.add_value('price', str(product['price'] / 100000))  # E.g.: '4349000' = '$43.49'
                yield loader.load_item()
