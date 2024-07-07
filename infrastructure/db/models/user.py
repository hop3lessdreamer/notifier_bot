""" User model description """

from sqlalchemy import BigInteger, Column, SmallInteger
from sqlalchemy.orm import relationship

from infrastructure.db.models.base import Base


class UserModel(Base):
    __tablename__ = 'User'

    ID = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    ChatID = Column(BigInteger, nullable=False)
    TZOffset = Column(SmallInteger, nullable=False)

    products = relationship('UserProductModel', back_populates='user', lazy='selectin')
