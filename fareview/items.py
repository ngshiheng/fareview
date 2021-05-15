import re

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from price_parser.parser import parse_price


def parse_name(name: str) -> str:
    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', name)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_non_word_characters = re.sub(r'[^a-zA-Z0-9%]', ' ', remove_brackets)
    remove_spaces = re.sub(' +', ' ', remove_non_word_characters)
    return remove_spaces


class FareviewItem(scrapy.Item):
    vendor = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    name = scrapy.Field(
        input_processor=MapCompose(parse_name),
        output_processor=TakeFirst(),
    )

    price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst(),
    )

    quantity = scrapy.Field(
        output_processor=TakeFirst(),
    )

    url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )
