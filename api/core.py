from typing import Tuple

from config.config import Settings
from api.utils.api_handler import APIInterface

settings = Settings()

headers = {
    "x-rapidapi-key": settings.api_key.get_secret_value(),
    "x-rapidapi-host": settings.host_api,
}
url = "https://" + settings.host_api

api = APIInterface()


def get_location_ids(city: str):
    """
    Получение городов
    """
    find_city = api.get_location()
    params = {"name": city, "locale": "ru"}
    # "locations",
    response = find_city("GET", url, headers, params, 3)
    try:
        response = response.json()
    except AttributeError:
        return []
    locations = dict()
    for location in response:
        locations[location["dest_id"]] = location["label"]
    return locations


def get_hotels(
    dest_id,
    checkin,
    checkout,
    person_count,
    limits: Tuple[int, int],
    filter_mode: str = "popularity",
):
    """
    Получения наиболее популярных отелей
    popularity - наиболее популярные
    distance - расстояние от центра города
    price - цена
    """
    find_hotels = api.get_best_hotel()
    params = {
        "checkout_date": str(checkout),
        "order_by": filter_mode,
        "filter_by_currency": "USD",
        "include_adjacency": "true",
        "categories_filter_ids": "class::2,class::4,free_cancellation::1",
        "room_number": "1",
        "dest_id": dest_id,
        "dest_type": "city",
        "adults_number": person_count,
        "page_number": "0",
        "checkin_date": str(checkin),
        "locale": "ru",
        "units": "metric",
    }
    print(params)
    response = find_hotels("GET", url, headers, params, 5)
    try:
        response = response.json()["result"]
    except AttributeError:
        return []
    hotels = []
    for hotel in response:
        hotels.append(
            {
                "id": hotel["hotel_id"],
                "title": hotel["hotel_name_trans"],
                "url": hotel["url"],
                "description": hotel_desc(hotel["hotel_id"]),
                "price": round(float(hotel["min_total_price"]), 2),
                "photos": hotel_photos(hotel["hotel_id"]),
                "address": hotel["address_trans"],
                "distance_to_cc": hotel["distance_to_cc"],
                "coordinates": [hotel["latitude"], hotel["longitude"]],
                "city": hotel["city_trans"],
                "checkin": str(checkin),
                "checkout": str(checkout),
            }
        )
    min_price, max_price = limits
    hotels = [hotel for hotel in hotels if min_price < hotel["price"] < max_price]
    return hotels


def hotel_photos(hotel_id):
    """
    Получение фотографий отеля
    """
    photos_hotel = api.get_hotel_photo()
    params = {"hotel_id": hotel_id, "locale": "ru"}
    response = photos_hotel("GET", url, headers, params, 5)
    try:
        response = response.json()
    except AttributeError:
        return []
    photos_urls = [pic["url_max"] for pic in response]
    return photos_urls


def hotel_desc(hotel_id):
    """
    Получение описания отеля
    """
    desc_hotel = api.get_hotel_desc()
    params = {"hotel_id": hotel_id, "locale": "ru"}
    response = desc_hotel("GET", url, headers, params, 3)
    try:
        response = response.json()
    except AttributeError:
        return []
    return response["description"]


if __name__ == "__main__":
    api()
    get_location_ids()
    get_hotels()
    hotel_photos()
    hotel_desc()
