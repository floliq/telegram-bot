from api.core import api, url, headers, get_location_ides, get_hotels
from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def exact_location_keygen(city):
    keyboard = InlineKeyboardMarkup(row_width=2)
    cities = get_location_ides(city)
    for dest_id, name in cities.items():
        keyboard.add(InlineKeyboardButton(text=name, callback_data=f"loc{dest_id}"))

    # for lat, lng, name in get_nearest_hotels(location):
    #     keyboard.add(InlineKeyboardButton(text=name, callback_data=exact_location_keygen(f"{lat},{lng}")))
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return keyboard


def hotel_card_keygen(dest_id):
    keyboard = InlineKeyboardMarkup()
    # hotel['hotel_name_trans']
    # hotel['url']
    # hotel['price_min']
    # hotel['price_max']
    # hotel['rating']
    # hotel['rating_count']
    # hotel['distance']
    # hotel['star_rating']
    # hotel['hotel_id']
    # hotel['image_url']
    # hotel['hotel_name_trans']
    # hotel['is_free_cancellation']
    # hotel['is_direct_booking']
    # hotel['is_superior']
    # hotel['is_premium']
    # hotel['is_luxury']
    # hotel['is_superior_luxury']
    # hotel['is_family']
    # hotel['is_superior_family']
    # hotel['is_premium_family']
    # hotel['is_luxury_family']
    # hotel['is_superior_luxury_family']
    # hotel['is_hotel_club']
    hotels = get_hotels(dest_id)
    for hotel in hotels:
        keyboard.add(InlineKeyboardButton(text=hotel, callback_data="hotel"))

    return keyboard


# api.core все запросы там
