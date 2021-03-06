import logging
import re
from typing import Optional, Union

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
    is_n_package = re.search(r'(\d{1,2}) ?(?:Bottle|Btl|Can|Case|Pack|Pint)', raw_name, flags=re.IGNORECASE)
    if is_n_package:
        return int(is_n_package.group(1))

    # Carlsberg Smooth Draught Beer Can, 320ml [Bundle of 24]
    is_package_of_n = re.search(r'(?:Bundle|Case|Pack|Package|Pint) of (\d{1,2})', raw_name, flags=re.IGNORECASE)
    if is_package_of_n:
        return int(is_package_of_n.group(1))

    # Heineken Can 2 Carton 48x330ml imported
    is_n_carton = re.search(r'(\d{1,2}) ?(?:Carton|Ctn)', raw_name, flags=re.IGNORECASE)
    if is_n_carton:
        return int(is_n_carton.group(1)) * 24

    # Tiger Lager Beer Can 40x320ml, Guinness Foreign Extra Stout 24 x 500ml
    is_ml = re.search(r'(\d{1,2}) ?[x] ?\d{3} ?ml', raw_name, flags=re.IGNORECASE)
    if is_ml:
        return int(is_ml.group(1))

    # Heineken Beer 330ml x 24 can
    is_ml_reverse = re.search(r'ml ?[x] ?(\d{1,2}) ?', raw_name, flags=re.IGNORECASE)
    if is_ml_reverse:
        return int(is_ml_reverse.group(1))

    return 1
