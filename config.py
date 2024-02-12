""" App Config """

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    MODE: str

    LOG_PATH: str
    LOG_LEVEL: str

    DB_PATH: str
    DB_NAME: str

    API_TOKEN: str
    PRICE_CHECKS_FREQUENCY: int

    #   when testing change to ".test.env"
    model_config = SettingsConfigDict(env_file='.test.env')

    @property
    def db_url_async(self) -> str:
        return f'sqlite+aiosqlite:///{self.DB_PATH}/{self.DB_NAME}'

    @property
    def db_url_sync(self) -> str:
        return f'sqlite:///{self.DB_PATH}/{self.DB_NAME}'


bot_config = BotConfig()
