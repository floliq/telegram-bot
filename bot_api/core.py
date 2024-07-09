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
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return keyboard


def hotel_card_keygen(dest_id):
    keyboard = InlineKeyboardMarkup()
    hotels = get_hotels(dest_id)
    for hotel in hotels:
        keyboard.add(InlineKeyboardButton(text=hotel, callback_data="hotel"))

    return keyboard


# api.core все запросы там
