import logging
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from fareview.items import FareviewItem
from fareview.models import Price, Product, create_table, db_connect

logger = logging.getLogger(__name__)


class ExistingProductPricePipeline:
    """
    Update existing products information
    Create a new price for existing products if the new price differs from the existing price

    `brand`, `url` and `quantity` is used to define the uniqueness of a product
    Using `url` alone isn't enough because the same URL (product) can have type of different `quantity`
    E.g.: "Pabst Blue Ribbon American Lager" can be of 'Single', '6 Packs' or 'Case of 24'

    Do not use `name` because name can change on a website
    """

    def __init__(self) -> None:
        """
        Initializes database connection and sessionmaker
        """
        self.engine = db_connect()
        create_table(self.engine)

        self.prices = []
        self.products_update = []

    def process_item(self, item: FareviewItem, spider: Spider) -> FareviewItem:
        assert spider
        adapter = ItemAdapter(item)

        name = adapter['name']
        brand = adapter['brand']
        url = adapter['url']
        quantity = adapter['quantity']
        price = adapter['price']

        new_price = float(price.amount)  # `.amount` is type of `<class 'decimal.Decimal'>`

        Session = sessionmaker(bind=self.engine)

        with Session.begin() as session:
            existing_product = session.query(Product).filter_by(brand=brand, url=url, quantity=quantity).one_or_none()

        if existing_product is not None:
            # Always update information for existing products
            product_to_update = dict(
                id=existing_product.id,
                name=name,
                volume=adapter.get('volume'),
                review_count=adapter.get('review_count'),
                attributes=adapter.get('attributes'),
            )
            self.products_update.append(product_to_update)

            # Create new price object for the product
            if existing_product.last_price != new_price:
                price = dict(
                    product_id=existing_product.id,
                    price=new_price,
                )
                self.prices.append(price)

            raise DropItem(f'Dropping item <{url}> here after update. We do not want duplicated products to be created in the following pipeline.')

        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Saving all the scraped products and prices in bulk on spider close event
        We use `bulk_insert_mappings` instead of `bulk_save_objects` here as it accepts lists of plain Python dictionaries which results in less amount of overhead associated with instantiating mapped objects and assigning state to them, they are faster
        """
        Session = sessionmaker(bind=self.engine)

        with Session.begin() as session:
            session.bulk_update_mappings(Product, self.products_update)
            logger.info(f'Updated {len(self.products_update)} existing products information in bulk.')

            prices = {frozenset(price.items()): price for price in self.prices}.values()  # Remove duplicated dict in a list. Only works if all values in dict are hashable. Reference: https://www.geeksforgeeks.org/python-removing-duplicate-dicts-in-list/
            session.bulk_insert_mappings(Price, prices)
            session.commit()
            logger.info(f'Created {len(self.prices)} new prices in bulk for existing products to the database.')


class NewProductPricePipeline:
    """
    Main pipeline that saves new products and their prices into database
    """

    def __init__(self) -> None:
        """
        Initializes database connection and sessionmaker
        """
        self.engine = db_connect()
        create_table(self.engine)

        self.products: list[dict[str, Any]] = []

    def process_item(self, item: FareviewItem, spider: Spider) -> FareviewItem:
        """
        This method is called for every item pipeline component
        We save each product as a dict in `self.products` list so that it later be used for bulk saving
        """
        assert spider
        adapter = ItemAdapter(item)

        # `_unique_id` is used to be hashed so that we can identify uniqueness of products using 3 main attributes: url, quantity, and brand.
        _unique_id = str(adapter['brand'] + adapter['url'] + str(adapter['quantity']))

        product = dict(
            _unique_id=hash(_unique_id),
            platform=adapter['platform'],
            name=adapter['name'],
            brand=adapter['brand'],
            vendor=adapter['vendor'],
            url=adapter['url'],
            quantity=adapter['quantity'],
            volume=adapter.get('volume'),
            review_count=adapter.get('review_count'),
            attributes=adapter.get('attributes'),
            price=adapter['price'].amount,
        )

        self.products.append(product)

        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Saving all the scraped products and prices in bulk on spider close event

        Sadly we currently have to use `return_defaults=True` while bulk saving Product objects which greatly reduces the performance gains of the bulk operation
        Though prices do get inserted to the DB in bulk

        Reference: https://stackoverflow.com/questions/36386359/sqlalchemy-bulk-insert-with-one-to-one-relation
        """
        Session = sessionmaker(bind=self.engine)

        with Session.begin() as session:
            products = {
                product['_unique_id']: product
                for product in self.products
            }.values()

            session.bulk_insert_mappings(Product, products, return_defaults=True)  # Set `return_defaults=True` so that PK (inserted one at a time) value is available for FK usage at another table

            prices = [dict(price=product['price'], product_id=product['id']) for product in products]
            session.bulk_insert_mappings(Price, prices)
            session.commit()

            logger.info(f'Created {len(products)} new products in bulk operation to the database.')
            logger.info(f'Created {len(prices)} new prices in bulk operation to the database.')
