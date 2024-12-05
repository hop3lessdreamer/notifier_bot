""" App Config """

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    MODE: str

    LOG_PATH: str
    LOG_LEVEL: str

    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    RABBIT_LOGIN: str
    RABBIT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT: str
    RABBIT_MONITOR_PORT: str

    API_TOKEN: str
    PRICE_CHECKS_FREQUENCY: int

    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBAPP_HOST: str
    WEBAPP_PORT: str

    #   TODO: when testing change to ".test.env"
    model_config = SettingsConfigDict(env_file='.prod.env')

    @property
    def postgres_sync(self) -> str:
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@localhost/{self.DB_NAME}'

    @property
    def postgres_async(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@localhost/{self.DB_NAME}'

    @property
    def webhook_url(self) -> str:
        return f'{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}'

    @property
    def price_check_frequency(self) -> int:
        return self.PRICE_CHECKS_FREQUENCY * 60


bot_config = BotConfig()  # type: ignore
test_config = BotConfig(_env_file='.test.env')
