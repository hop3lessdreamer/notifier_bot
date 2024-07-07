""" Product model description """

from sqlalchemy import BLOB, BigInteger, Column, Numeric, String
from sqlalchemy.orm import relationship

from infrastructure.db.models.base import Base


class ProductModel(Base):
    __tablename__ = 'Product'

    ID = Column(BigInteger, primary_key=True, autoincrement='auto')
    Price = Column(Numeric, nullable=False)
    Img = Column(BLOB, nullable=False)
    Title = Column(String(255), nullable=False)

    users = relationship('UserProductModel', back_populates='product', lazy='selectin')
