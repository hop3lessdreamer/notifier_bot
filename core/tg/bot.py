from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import bot_config

bot = Bot(bot_config.API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
