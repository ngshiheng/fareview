import logging
import os
import re

import scrapy
from scrapy.downloadermiddlewares.retry import get_retry_request
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
        'DOWNLOAD_DELAY': os.environ.get('SHOPEE_DOWNLOAD_DELAY', 60),
        'DOWNLOADER_MIDDLEWARES': {
            **settings.get('DOWNLOADER_MIDDLEWARES'),
            'fareview.middlewares.DelayedRequestsMiddleware': 100,
        },
    }

    start_urls = [
        f'https://shopee.sg/api/v4/search/search_items?by=sales&categoryids=100860&keyword={keyword}&limit=60&newest=0&order=desc&page_type=search&rating_filter=4&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2'
        for keyword in settings.get('SUPPORTED_BRANDS')
    ]

    headers = {
        'af-ac-enc-dat': 'AAcyLjUuMC0yAAABhTHNY+IAAA8RAuAAAAAAAAAAAuvlR3weVVU60ykHUkkzSmQs+0sol/82EyfDx/bVRcPaaRvYm2HbOiPVt6hB0HAjTAwjYX8IWDX7g61V4QmAQAFLKauqoRk96ECw69dLQlYAAnQoRmv3CKlElgGaoKX5ImIkf0MZlcTrh+nB0CBEt+gDEF5l14gn7zv27hzgjt6hN8APdyIegnbmhFArdL/RxUry9cOMycxsdIDQM+ODTHGp53b+AN533ToSyEq5XNpJg4KJ+7GBSK6XH2g0CbfqVYn9F+uHgnOMbQmJ0DN0C8bvxcKLBZhmwdiP6VgaEoKkhMgonF/+wozCuUFxKBrQw44hMGaX/zYTJ8PH9tVFw9ppG9ibFL6FFVtxdrgfhUe1x1h3rw7kzL3gRGGMPpQYugB7di11yWs8g5EXgCo7x09f4CdFdG9DB38nh65U6+o94yEt3oO7i5suvhtxQ4sEDZzZuZ3hW60K+smhOYYGQH4w44WxN7O7IofDww1wM/r+pufhJkatt8la5FiUWn4nS1xSTq8akFOHlP+z7E50wqb06wIKzOhSEoCDq8ldg+RcTmGj6lzRcbx+u+wuFArvx+zvDDADUzAo7YpZrzJG3NU1I8Tny8W6LkL4KiSFzjuz0gQUix0M3gtM3QNLkWnZ3uivVKpHavivIHolfOCd7veQccOb8MS3gD4Lv0cZsWDYYHdpR1c3Np8BzcsRRPm/ZZgFLUkcF6sQRVOFZERU8tJ5ZczdgB1xOGqN7PIb94O08sVSMFzRcbx+u+wuFArvx+zvDDC0y5WLb/4O97leNkLwzVk+3whGcRbtuybBi/nvnxi60Fy7UBsXQP/li7TBps6nqhXRHJJ2HKErNOh5euwKv/tW29epMeIAg6F91FIObWlA4cloO/QLz/E2Q7O4muXDQ8JIA/TtWmBoI5o7mG3pL/q/eKwBEqMBKXUHgceF9ulY2PKdmalj/urvofGc5w+3XtJeyyxpna6kuPaep/AiH6HE',
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
        data = response.json()
        if 'items' not in data:
            error = f'Challenged by Shopee. URL <{response.request.url}>. Request headers <{response.request.headers}>.'

            retry_request = get_retry_request(response.request, reason=error, spider=self)
            if retry_request:
                yield retry_request
            return

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
