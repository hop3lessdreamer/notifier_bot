""" User model description """

from sqlalchemy import Column, BigInteger, SmallInteger
from sqlalchemy.orm import relationship

from db.models.base import Base


class UserModel(Base):
    __tablename__ = 'User'

    ID = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    TZOffset = Column(SmallInteger, nullable=False)

    products = relationship('UserProductModel', back_populates='user', lazy='selectin')
