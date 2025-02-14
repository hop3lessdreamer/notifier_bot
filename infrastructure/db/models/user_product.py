""" UserProduct model description """

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from infrastructure.db.models.base import Base


class UserProductModel(Base):
    __tablename__ = 'UserProduct'

    UserID = Column(BigInteger, ForeignKey('User.ID'), primary_key=True)
    ProductID = Column(BigInteger, ForeignKey('Product.ID'), primary_key=True)
    PriceThreshold = Column(Numeric)
    Added = Column(DateTime, nullable=False)
    Changed = Column(DateTime)

    user = relationship('UserModel', back_populates='products', lazy='selectin')
    product = relationship('ProductModel', back_populates='users', lazy='selectin')
