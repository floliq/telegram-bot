from config.config import Settings
from api.utils.api_handler import APIInterface

settings = Settings()

headers = {
    "x-rapidapi-key": settings.api_key.get_secret_value(),
    "x-rapidapi-host": settings.host_api,
}
url = "https://" + settings.host_api

api = APIInterface()

if __name__ == "__main__":
    api()
