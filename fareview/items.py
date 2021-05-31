import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from price_parser.parser import parse_price

from fareview.utils.parsers import parse_name, parse_quantity, parse_volume


class FareviewItem(scrapy.Item):
    platform = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    # Product
    name = scrapy.Field(
        input_processor=MapCompose(parse_name),
        output_processor=TakeFirst(),
    )

    brand = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    vendor = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst(),
    )

    quantity = scrapy.Field(
        input_processor=MapCompose(parse_quantity),
        output_processor=TakeFirst(),
    )

    volume = scrapy.Field(
        input_processor=MapCompose(parse_volume),
        output_processor=TakeFirst(),
    )

    review_count = scrapy.Field(
        output_processor=TakeFirst(),
    )

    attributes = scrapy.Field(
        output_processor=TakeFirst(),
    )

    # Price
    price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst(),
    )
