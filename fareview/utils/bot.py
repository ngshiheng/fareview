import logging
from datetime import datetime, timedelta
from typing import Dict, List

from fareview.models import Product, db_connect
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def create_price_alert_payload(brands: List[str]) -> list:
    engine = db_connect()
    session = sessionmaker(bind=engine)()

    try:
        products = []
        for brand in session.query(Product.brand).distinct():
            for volume in session.query(Product.volume).distinct():
                product = session.query(Product).filter(
                    Product.updated_on >= datetime.utcnow() - timedelta(days=1),
                    Product.brand == brand.brand,
                    Product.quantity == 24,  # NOTE: We only care about cartons
                    Product.volume == volume.volume,
                ).order_by(Product.last_price).first()

                if product:
                    products.append(product)

        return products

    except Exception as error:
        logger.exception(error)
        raise

    finally:
        session.close()
