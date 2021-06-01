import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fareview.models import Product, db_connect
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """
    Helper function for formatting the gathered user info.
    """
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def create_price_alert_summary(brands: Optional[List[str]] = None) -> Dict[str, List]:
    engine = db_connect()
    session = sessionmaker(bind=engine)()

    # If user did not specify which brand alerts to receive, we shall send them everything
    if not brands:
        brands = [brand.brand for brand in session.query(Product.brand).distinct()]

    try:
        products = []
        for brand in brands:
            for distinct_volume in session.query(Product.volume).distinct():
                product = session.query(Product).filter(
                    Product.updated_on >= datetime.utcnow() - timedelta(days=1),
                    Product.brand == brand,
                    Product.quantity == 24,  # NOTE: We only care about products where their quantity is 24
                    Product.volume == distinct_volume.volume,
                ).order_by(Product.last_price).first()

                if product:
                    products.append(
                        {
                            'platform': product.platform,
                            'vendor': product.vendor,
                            'name': product.name,
                            'brand': product.brand,
                            'volume': product.volume,
                            'price': product.last_price,
                        }
                    )

        result = defaultdict(list)

        # Group product summary results by `brand` name
        for p in products:
            result[p['brand']].append(p)

        return result

    except Exception as error:
        logger.exception(error)
        raise

    finally:
        session.close()
