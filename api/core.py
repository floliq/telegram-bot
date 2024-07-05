from config.config import Settings
from api.utils.api_handler import APIInterface

settings = Settings()

headers = {
    "x-rapidapi-key": settings.api_key.get_secret_value(),
    "x-rapidapi-host": settings.host_api,
}
url = "https://" + settings.host_api

api = APIInterface()


def get_location_ides(city: str):
    """
    Получение городов
    """
    find_city = api.get_location()
    params = {"name": city, "locale": "en-gb"}
    response = find_city("GET", url, headers, params, 5).json()
    print(response)
    locations = dict()
    for location in response:
        locations[location["dest_id"]] = location["label"]
    return locations


def get_hotels(dest_id):
    """
    Получения наиболее популярных отелей
    """
    find_hotels = api.get_best_hotel()
    params = {
        "checkout_date": "2024-09-15",
        "order_by": "popularity",
        "filter_by_currency": "AED",
        "include_adjacency": "true",
        "categories_filter_ids": "class::2,class::4,free_cancellation::1",
        "room_number": "1",
        "dest_id": dest_id,
        "dest_type": "city",
        "adults_number": "2",
        "page_number": "0",
        "checkin_date": "2024-09-14",
        "locale": "en-gb",
        "units": "metric",
    }
    response = find_hotels("GET", url, headers, params, 5)
    response = response.json()
    hotels = [hotel["hotel_name_trans"] for hotel in response["result"]]
    return hotels


def hotel_info(dest_id):
    """
    Получение названия, ссылки, адреса и локации отеля
    """
    info_hotel = api.get_hotel_info()
    params = {"hotel_id": dest_id, "locale": "en-gb"}
    response = info_hotel("GET", url, headers, params, 5)
    response = response.json()
    name = response["name"]
    link = response["url"]
    address = response["address"]
    location = [locate for locate in response["location"].values()]
    return name, link, address, location


def hotel_photos(dest_id):
    """
    Получение фотографий отеля
    """
    photos_hotel = api.get_hotel_photo()
    params = {"hotel_id": dest_id, "locale": "en-gb"}
    response = photos_hotel("GET", url, headers, params, 5)
    response = response.json()
    photos_urls = [pic["url_max"] for pic in response]
    return photos_urls


def hotel_desc(dest_id):
    """
    Получение описания отеля
    """
    desc_hotel = api.get_hotel_desc()
    params = {"hotel_id": dest_id, "locale": "en-gb"}
    response = desc_hotel("GET", url, headers, params, 5)
    response = response.json()
    return response["description"]


def get_all_hotel_info(dest_id):
    """
    Получение полной информации об отеле
    """
    name, link, address, location = hotel_info(dest_id)
    photos = hotel_photos(dest_id)
    desc = hotel_desc(dest_id)
    return name, link, address, location, photos, desc


if __name__ == "__main__":
    api()
    get_location_ides()
    get_hotels()
    hotel_info()
    hotel_photos()
    hotel_desc()
    get_all_hotel_info()
