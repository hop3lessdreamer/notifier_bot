""" BaseHandler """

from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiogram import Dispatcher

from db.queries import DBQueries


@dataclass
class BaseHandler(ABC):

    db: DBQueries
    dp: Dispatcher

    @abstractmethod
    def register_handlers(self): ...
