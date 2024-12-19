""" App Config """

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    MODE: str

    LOG_PATH: str
    LOG_LEVEL: str

    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str

    RABBIT_LOGIN: str
    RABBIT_PASS: str
    RABBIT_HOST: str
    RABBIT_PORT: str
    RABBIT_MONITOR_PORT: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str

    API_TOKEN: str

    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBAPP_HOST: str
    WEBAPP_PORT: str

    #   TODO: when testing change to ".test.env"
    model_config = SettingsConfigDict(env_file='.prod.env')

    @property
    def postgres_sync(self) -> str:
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}'

    @property
    def postgres_async(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}'

    @property
    def webhook_url(self) -> str:
        return f'{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}'


#   FIXME: требуется для CI/CD т.к в репе нет .prod.env, то при инициализации падает
try:
    bot_config = BotConfig()  # type: ignore
except Exception:
    bot_config = BotConfig(_env_file='.test.env')
test_config = BotConfig(_env_file='.test.env')
