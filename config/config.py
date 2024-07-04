import os
from dotenv import load_dotenv
from pydantic import SecretStr, StrictStr
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    api_key: SecretStr = os.getenv("API_KEY", None)
    host_api: StrictStr = os.getenv("BASE_URL", None)
    bot_token: SecretStr = os.getenv("BOT_TOKEN", None)
