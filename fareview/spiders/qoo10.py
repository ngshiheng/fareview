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
    name = 'qoo10'
    custom_settings = {
        'DOWNLOAD_DELAY': os.environ.get('QOO10_DOWNLOAD_DELAY', 5),
    }

    start_urls = ['https://www.qoo10.sg/gmkt.inc/Category/DefaultAjaxAppend.aspx?p=1&s=rv&v=lt&ct=300001029&ack=&ac=&f=st:SG|ct:300001029|&t=gc&pm=&cc=N&cb=N&cst=N']

    def parse(self, response):
        logger.info(response.request.headers)

        product_urls = response.xpath('//a[@class="lnk_vw"]/@href').getall()

        for url in product_urls:
            yield response.follow(url, callback=self.parse_product_details)

    def parse_product_details(self, response):
        loader = ItemLoader(item=FareviewItem(), selector=response)

        name = response.xpath('//h2[@class="name"]/text()').get()

        try:
            brand = next(brand for brand in ['tiger', 'heineken', 'carlsberg', 'guinness', 'asahi'] if brand in name.lower())

        except StopIteration:
            return

        attributes = dict()

        loader.add_value('platform', self.name)

        loader.add_value('name', name)
        loader.add_value('brand', brand)
        loader.add_xpath('vendor', '//div[@class="goods-shopinfo"]//a/text()')
        loader.add_value('url', response.request.url)

        raw_review_count = response.xpath('//em[@id="opinion_count"]/text()').get()
        review_count = int(re.sub(r'[^0-9]', '', raw_review_count))

        loader.add_value('quantity', name)
        loader.add_value('review_count', review_count)
        loader.add_value('attributes', attributes)

        loader.add_xpath('price', '//strong[@id="qprice_span"]/text()')
        yield loader.load_item()
