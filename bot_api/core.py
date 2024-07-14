from typing import *

from api.core import (
    api,
    url,
    headers,
    get_hotels,
)
from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def exact_location_keygen(cities):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for dest_id, name in cities.items():
        keyboard.add(InlineKeyboardButton(text=name, callback_data=f"loc{dest_id}"))
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return keyboard


#
def hotel_card_keygen(list_of_data: List[Dict], list_of_photos: List, card_index: int = 0, photo_index: int = 0):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Забронировать", callback_data="order"))
    if photo_index == 0 and len(list_of_photos) > (photo_index + 1):
        keyboard.add(
            InlineKeyboardButton("Следующее фото ➡️", callback_data='photo{}_{}'.format(photo_index+1, card_index))
        )
    elif photo_index == len(list_of_data) - 1:
        keyboard.add(
            InlineKeyboardButton("⬅️ Предыдущее фото", callback_data="photo" + str(photo_index - 1))
        )
    else:
        keyboard.row(
            InlineKeyboardButton("⬅️ Предыдущее фото", callback_data="photo" + str(photo_index - 1)),
            InlineKeyboardButton("Следующее фото ➡️", callback_data="photo" + str(photo_index + 1)),
        )
    if card_index == 0 and len(list_of_data) > (card_index + 1):
        keyboard.add(
            InlineKeyboardButton("Вперёд ➡️", callback_data="card" + str(card_index + 1))
        )
    elif card_index == len(list_of_data) - 1:
        keyboard.add(
            InlineKeyboardButton("⬅️ Назад", callback_data="card" + str(card_index - 1))
        )
    else:
        keyboard.row(
            InlineKeyboardButton("⬅️ Назад", callback_data="card" + str(card_index - 1)),
            InlineKeyboardButton("Вперёд ➡️", callback_data="card" + str(card_index + 1)),
        )
    return keyboard

# api.core все запросы там
