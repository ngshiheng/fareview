import logging
import re
from typing import Optional, Union
from urllib.parse import urlencode

from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

settings = get_project_settings()


def parse_name(raw_name: str) -> str:
    """
    Sanitize product name
    """
    logger.info(f'Parsing raw_name "{raw_name}".')

    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', raw_name)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_non_word_characters = re.sub(r'[^a-zA-Z0-9%.]', ' ', remove_brackets)
    remove_spaces = re.sub(' +', ' ', remove_non_word_characters)

    return remove_spaces.strip()


def parse_volume(raw_name: str) -> Optional[int]:
    """
    Get product volume from name
    """
    has_volume = re.search(r'(\d+) ?ml', raw_name, re.IGNORECASE)
    if has_volume:
        return int(has_volume.group(1))


def parse_quantity(raw_name: Union[str, int]) -> int:
    """
    Get product quantity from name
    """
    if isinstance(raw_name, int):
        return raw_name

    # Blue Moon Belgian White Wheat Ale 355ml x 24 Bottles
    is_bottle = re.search(r'(\d{1,2}) ?Bottle', raw_name, flags=re.IGNORECASE)
    if is_bottle:
        quantity = int(is_bottle.group(1))
        return quantity

    # Carlsberg 490ml x 24 Cans (BBD: Oct 2021)
    is_can = re.search(r'(\d{1,2}) ?Can', raw_name, flags=re.IGNORECASE)
    if is_can:
        return int(is_can.group(1))

    # Carlsberg Danish Pilsner Beer Can 490ml (Pack of 24) Green Tab
    is_pack = re.search(r'Pack of (\d+)', raw_name, flags=re.IGNORECASE)
    if is_pack:
        return int(is_pack.group(1))

    # Carlsberg Smooth Draught Beer Can, 320ml [Bundle of 24]
    is_bundle = re.search(r'Bundle of (\d+)', raw_name, flags=re.IGNORECASE)
    if is_bundle:
        return int(is_bundle.group(1))

    # Tiger Lager Beer Can 40x320ml, Guinness Foreign Extra Stout 24 x 500ml
    is_ml = re.search(r'(\d{1,2}) ?[x] ?', raw_name, flags=re.IGNORECASE)
    if is_ml:
        return int(is_ml.group(1))

    # Heineken Beer 330ml x 24 can
    is_ml_reverse = re.search(r' ?[x] ?(\d{1,2}) ?', raw_name, flags=re.IGNORECASE)
    if is_ml_reverse:
        return int(is_ml_reverse.group(1))

    # Carlsberg 490ml x 24 Cans (BBD: Oct 2021)
    is_case = re.search(r'(\d{1,2}) ?Case', raw_name, flags=re.IGNORECASE)
    if is_case:
        return int(is_case.group(1))

    return 1


def get_proxy_url(url: str) -> str:
    """
    We send all our requests to https://www.scraperapi.com/ API endpoint in order use their proxy servers
    This function converts regular URL to Scaper API's proxy URL
    """
    scraper_api_key = settings.get('SCRAPER_API_KEY')
    if not scraper_api_key:
        logger.warning('Scraper API key not set.', extra=dict(url=url))
        return url

    proxied_url = 'http://api.scraperapi.com/?' + urlencode({'api_key': scraper_api_key, 'url': url})
    logger.info(f'Scraping using Scraper API. URL <{url}>.')
    return proxied_url
