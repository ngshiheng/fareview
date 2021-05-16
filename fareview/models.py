import datetime

from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import JSON

settings = get_project_settings()

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(settings.get('DATABASE_CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, index=True)
    product = relationship('Product', backref='prices', cascade='delete')

    price = Column(Float)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return f'Price(price={self.price}, product={self.product.name})'


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (UniqueConstraint('url', 'quantity', 'brand'),)

    id = Column(Integer, primary_key=True)

    platform = Column(String())

    name = Column(String())
    brand = Column(String(), nullable=True, default=None)
    vendor = Column(String(), nullable=True, default=None)
    url = Column(String())

    quantity = Column(Integer(), default=1)
    review_count = Column(Integer, nullable=True, default=None)

    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.now)

    last_price = column_property(
        select([Price.price]).
        where(Price.product_id == id).
        order_by(Price.id.desc()).
        limit(1).  # NOTE: We have to always limit this as 1 to prevent `CardinalityViolation: more than one row returned by a subquery used as an expression`
        as_scalar()
    )

    attributes = Column(JSON, default=dict)

    def __repr__(self) -> str:
        return f'Product({self.name}, vendor={self.vendor})'
