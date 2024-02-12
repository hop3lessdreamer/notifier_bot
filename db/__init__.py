""" Initialization DB module """

from abc import ABC, abstractmethod

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import bot_config


class Database(ABC):

    __slots__ = ('async_sessionmaker', '_engine', '_aengine')

    def __init__(self) -> None:
        self.async_sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self._aengine: AsyncEngine | None = None
        self._engine: Engine | None = None

    async def __call__(self) -> AsyncSession:
        if not self.async_sessionmaker:
            raise ValueError("async_sessionmaker not available. Run setup() first.")

        # async with self.async_sessionmaker() as session:
        #     async with session.begin():
        #         yield session
        return self.async_sessionmaker()

    @property
    @abstractmethod
    def engine(self) -> Engine | None:
        return self._engine

    @property
    @abstractmethod
    def aengine(self) -> AsyncEngine | None:
        return self._aengine

    @abstractmethod
    def setup(self) -> None:
        raise NotImplementedError


class SQLiteDatabase(Database):
    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(bot_config.db_url_sync, echo=True)
        return self._engine

    @property
    def aengine(self) -> AsyncEngine:
        if self._aengine is None:
            self._aengine = create_async_engine(bot_config.db_url_async, echo=True)
        return self._aengine

    def setup(self) -> None:
        self.async_sessionmaker = async_sessionmaker(
            bind=self.aengine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    def init_db(self, base: DeclarativeBase) -> None:
        with self.engine.begin() as e:
            base.metadata.create_all(e)

    def drop_db(self, base: DeclarativeBase) -> None:
        with self.engine.begin() as e:
            base.metadata.drop_all(e)

    def session(self) -> Session:
        return sessionmaker(bind=self.engine)()


db: SQLiteDatabase = SQLiteDatabase()
db.setup()
# session: AsyncIterator[AsyncSession] = db()
