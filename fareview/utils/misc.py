import logging
from datetime import datetime, timedelta

from fareview.models import Price, Product, db_connect
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

logger = logging.getLogger(__name__)


Session = scoped_session(sessionmaker(bind=db_connect()))


def remove_stale_products_prices(stale_days: int = 7) -> None:
    """
    Remove stale products and prices which are not updated for N number of days
    """
    assert isinstance(stale_days, int) and stale_days >= 7, 'Invalid `stale_days` input.'

    with Session() as session:
        stale_products = session.query(Product).filter(Product.updated_on <= datetime.utcnow() - timedelta(days=stale_days))
        stale_products_count = stale_products.count()
        logger.info(f'Found {stale_products_count} stale products.')

        if stale_products_count < 1:
            logger.info('No stale products to delete.')
            return

        product_ids = [product.id for product in stale_products.all()]
        stale_prices = session.query(Price).filter(Price.product_id.in_(product_ids))
        logger.info(f'Found {stale_prices.count()} stale prices.')

        stale_prices.delete()
        stale_products.delete()
        session.commit()

        logger.info(f'{stale_products_count} stale products deleted successfully.')
