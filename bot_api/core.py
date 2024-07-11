from api.core import api, url, headers, get_location_ides, get_all_hotel_info, get_hotels
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


def hotel_card_keygen(list_of_data, n, flag_step="card"):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Забронировать", callback_data="order"))
    if n == 0 and len(list_of_data) > (n + 1):
        keyboard.add(InlineKeyboardButton("Вперёд ➡️", callback_data=flag_step + str(n + 1)))
    elif n == len(list_of_data) - 1:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=flag_step + str(n - 1)))
    else:
        keyboard.row(
            InlineKeyboardButton("⬅️ Назад", callback_data=flag_step + str(n - 1)),
            InlineKeyboardButton("Вперёд ➡️", callback_data=flag_step + str(n + 1))
        )
    return keyboard


# api.core все запросы там
