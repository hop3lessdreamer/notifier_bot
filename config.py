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

    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBAPP_HOST: str
    WEBAPP_PORT: str

    #   TODO: when testing change to ".test.env"
    model_config = SettingsConfigDict(env_file='.prod.env')

    @property
    def db_url_async(self) -> str:
        return f'sqlite+aiosqlite:///{self.DB_PATH}/{self.DB_NAME}'

    @property
    def db_url_sync(self) -> str:
        return f'sqlite:///{self.DB_PATH}/{self.DB_NAME}'

    @property
    def webhook_url(self) -> str:
        return f'{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}'

    @property
    def price_check_frequency(self) -> int:
        return self.PRICE_CHECKS_FREQUENCY * 60


bot_config = BotConfig()  # type: ignore
