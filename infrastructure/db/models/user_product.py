""" UserProduct model description """

from sqlalchemy import DDL, BigInteger, Column, DateTime, ForeignKey, Numeric, event
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


# @event.listens_for(UserProductModel.__table__, 'after_create')
# def trg_create(target, connection, **kw):
#     connection.execute(
#         """
#         CREATE TRIGGER user_product_check_fkeys
#             BEFORE INSERT ON "UserProduct"
#             FOR EACH ROW
#             BEGIN
#                 SELECT RAISE(ABORT, 'Внешний ключ не существует в ссылочной таблице')
#                 WHERE
#                     (SELECT COUNT(*) FROM "User" u WHERE u."ID" = NEW."UserID") = 0
#                     or (SELECT COUNT(*) FROM "Product" p WHERE p."ID" = NEW."ProductID") = 0;
#             END;
#         """
#     )

trigger = DDL(
    """
    CREATE TRIGGER user_product_check_fkeys
        BEFORE INSERT ON "UserProduct"
        FOR EACH ROW
        BEGIN
            SELECT RAISE(ABORT, 'Внешний ключ не существует в ссылочной таблице')
            WHERE
                (SELECT COUNT(*) FROM "User" u WHERE u."ID" = NEW."UserID") = 0
                or (SELECT COUNT(*) FROM "Product" p WHERE p."ID" = NEW."ProductID") = 0;
        END;
    """
)


event.listen(UserProductModel.__table__, 'after_create', trigger)
