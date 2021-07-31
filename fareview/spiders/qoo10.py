import logging
import os
import re

import scrapy
from fareview.items import FareviewItem
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


class Qoo10Spider(scrapy.Spider):
    """
    Priority of getting price of product:
    Daily Deal -> Q-Price -> Retail Price
    """
    name = 'qoo10'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('QOO10_DOWNLOAD_DELAY', 5),
    }

    start_urls = ['https://www.qoo10.sg/gmkt.inc/Category/DefaultAjaxAppend.aspx?p=1&s=rv&v=lt&ct=300001029&ack=&ac=&f=st:SG|ct:300001029|&t=gc&pm=&cc=N&cb=N&cst=N']

    def parse(self, response):
        """
        @url https://www.qoo10.sg/gmkt.inc/Category/DefaultAjaxAppend.aspx?p=1&s=rv&v=lt&ct=300001029&ack=&ac=&f=st:SG|ct:300001029|&t=gc&pm=&cc=N&cb=N&cst=N
        @returns requests 1
        """
        logger.info(response.request.headers)
        logger.info(response.ip_address)

        product_urls = response.xpath('//a[@class="lnk_vw"]/@href')
        yield from response.follow_all(product_urls, cookies={'gmktCurrency': 'SGD'}, callback=self.parse_product_details)

    def parse_product_details(self, response):
        loader = ItemLoader(item=FareviewItem(), selector=response)

        name = response.xpath('//h2[@class="goods-detail__name"]/text()').get()
        if not name:
            logger.warning('Name is None')
            return

        # Skip product if it's not in `SUPPORTED_BRANDS`
        remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', name)
        brand = next((brand for brand in settings['SUPPORTED_BRANDS'] if brand in remove_brackets.lower()), None)
        if brand is None:
            return

        # Skip price if it's 'Sold Out'
        raw_prices = response.xpath('//li[@id="ph_GoodsPriceInfoSection"]//*[contains(text(),"S$")]//text()')
        price = raw_prices[-1].get() if raw_prices else response.xpath('//div[@class="prc"]//strong//text()').get()
        if price == 'Sold Out':
            return

        raw_sold = response.xpath('//div[@class="goods-shopsatis__num"]/strong/text()').get()
        sold = int(re.sub(r'[^0-9]', '', raw_sold)) if raw_sold else None

        attributes = dict(
            sold=sold,
        )

        loader.add_value('platform', self.name)

        loader.add_value('name', name)
        loader.add_value('brand', brand)
        loader.add_xpath('vendor', '//a[@id="shop_link"]/@title')
        loader.add_value('url', response.request.url)

        raw_review_count = response.xpath('//em[@id="opinion_count"]/text()').get()
        review_count = int(re.sub(r'[^0-9]', '', raw_review_count))

        loader.add_value('quantity', name)
        loader.add_value('volume', name)
        loader.add_value('review_count', review_count)
        loader.add_value('attributes', attributes)

        loader.add_value('price', price)
        yield loader.load_item()
