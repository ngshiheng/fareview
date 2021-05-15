import logging
import re

logger = logging.getLogger(__name__)


def parse_name(raw_name: str) -> str:
    """
    Sanitize product name
    """
    logger.info(f'Raw Name = "{raw_name}"')
    remove_brackets = re.sub(r'[\(\[].*?[\]\)]', '', raw_name)  # E.g.: "Somersby Blackberry Cider [CANS] 330ml"
    remove_non_word_characters = re.sub(r'[^a-zA-Z0-9%]', ' ', remove_brackets)
    remove_spaces = re.sub(' +', ' ', remove_non_word_characters)
    return remove_spaces


def parse_quantity(raw_name: str) -> int:
    """
    Get product quantity from name
    """
    logger.info(f'Raw Name = "{raw_name}"')

    # Hite Jinro Extra Cold Beer Single Carton
    if 'carton' in raw_name.lower():
        return 24

    # [Bundle of 24] Sapporo Premium Can Beer 330ml x 24cans (Expiry Jan 22)
    is_pack = re.search(r'Bundle of (\d+)', raw_name, flags=re.IGNORECASE)
    if is_pack:
        return int(is_pack.group(1))

    # Carlsberg Danish Pilsner Beer Can 490ml (Pack of 24) Green Tab
    is_pack = re.search(r'Pack of (\d+)', raw_name, flags=re.IGNORECASE)
    if is_pack:
        return int(is_pack.group(1))

    # Tiger Lager Beer Can 40x320ml, Guinness Foreign Extra Stout 24 x 500ml
    is_ml = re.search(r'(\d+)\s?x\s?\d{3}ml', raw_name, flags=re.IGNORECASE)
    if is_ml:
        return int(is_ml.group(1))

    # Heineken Beer 330ml x 24 can
    is_ml_reverse = re.search(r'\d{3}ml\s?x\s?(\d+)', raw_name, flags=re.IGNORECASE)
    if is_ml_reverse:
        return int(is_ml_reverse.group(1))

    # Blue Moon Belgian White Wheat Ale 355ml x 24 Bottles
    is_pack = re.search(r'(\d+)(?:[A-Za-z\s]|\s)+Bottle(s?)', raw_name, flags=re.IGNORECASE)
    if is_pack:
        quantity = int(is_pack.group(1))
        return quantity

    # San Miguel Pale Pilsen Can (24 cans x 330ml)
    is_cans = re.search(r'(\d+) Cans', raw_name, flags=re.IGNORECASE)
    if is_cans:
        return int(is_cans.group(1))

    return 1
