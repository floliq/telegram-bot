from typing import *
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def exact_location_keygen(cities):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for dest_id, name in cities.items():
        keyboard.add(InlineKeyboardButton(text=name, callback_data=f"loc{dest_id}"))
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return keyboard


def exact_history_list(history):
    keyboard = InlineKeyboardMarkup()
    for id, values in history.items():
        city = values["search_result"][0]["city"]
        date = values["date_time"].strftime("%d.%m.%Y %H:%M:%S")
        keyboard.add(
            InlineKeyboardButton(text=f"{city} {date}", callback_data=f"his{id}")
        )
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return keyboard


def hotel_card_keygen(
    list_of_data: List[Dict],
    list_of_photos: List,
    url: str,
    card_index: int = 0,
    photo_index: int = 0,
):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Забронировать", url=url))
    if photo_index == 0 and len(list_of_photos) > (photo_index + 1):
        keyboard.add(
            InlineKeyboardButton(
                "Следующее фото ➡️",
                callback_data="photo{}_{}".format(photo_index + 1, card_index),
            )
        )
    elif photo_index == len(list_of_data) - 1:
        keyboard.add(
            InlineKeyboardButton(
                "⬅️ Предыдущее фото",
                callback_data="photo{}_{}".format(photo_index - 1, card_index),
            )
        )
    else:
        keyboard.row(
            InlineKeyboardButton(
                "⬅️ Предыдущее фото",
                callback_data="photo{}_{}".format(photo_index - 1, card_index),
            ),
            InlineKeyboardButton(
                "Следующее фото ➡️",
                callback_data="photo{}_{}".format(photo_index + 1, card_index),
            ),
        )
    if card_index == 0 and len(list_of_data) > (card_index + 1):
        keyboard.add(
            InlineKeyboardButton(
                "Вперёд ➡️", callback_data="card{}".format(card_index + 1)
            )
        )
    elif card_index == len(list_of_data) - 1:
        keyboard.add(
            InlineKeyboardButton(
                "⬅️ Назад", callback_data="card{}".format(card_index + 1)
            )
        )
    else:
        keyboard.row(
            InlineKeyboardButton(
                "⬅️ Назад", callback_data="card{}".format(card_index + 1)
            ),
            InlineKeyboardButton(
                "Вперёд ➡️", callback_data="card{}".format(card_index + 1)
            ),
        )
    return keyboard
