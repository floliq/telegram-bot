import json

import requests
from telebot.types import Message, InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime

from api.core import get_location_ids, hotel_photos, get_hotels
from database.common.models import db, User, History
from tg_api.common.bot_init import bot
from bot_api.core import *
from database.core import crud


db_write = crud.create()
db_read = crud.retrieve()
check_exists_data = crud.check_exists()
update = crud.update_row()


@bot.message_handler(commands=["start", "help", "history"])
def send_welcome(message: Message):
    """
    /start and /help bot commands
    :param message:
    :return:
    """
    if not check_exists_data(db, User, User.chat_id == message.chat.id):
        db_write(db, User, {"chat_id": message.chat.id})
    if "start" in message.text:
        bot.send_message(
            message.chat.id,
            "Приветствую в боте по поиску отелей. Начните с команды /help.",
        )
        update(db, User, User.chat_id == message.chat.id, {"action": 0})
    elif "help" in message.text:
        bot.send_message(
            message.chat.id,
            "Используйте следующие команды:\n"
            "/help - получить справку\n"
            "/lowprice - отели с низкими ценами\n"
            "/guest_rating - самые популярные отели\n"
            "/bestdeal - отели ближе всего к центру\n"
            "/history - история запросов",
        )
    elif "history" in message.text:
        bot.send_message(
            message.chat.id,
            "Отображение вашей истории пользования, подождите пожалуйста...",
        )
        query = (
            History.select(History.id, History.date_time, History.search_result)
            .join(User)
            .where((User.chat_id == message.chat.id) & (History.event == "hotels"))
        )

        # Execute the query
        search_results = {
            result.id: {
                "search_result": json.loads(result.search_result),
                "date_time": result.date_time,
            }
            for result in query
        }
        if search_results:
            bot.send_message(
                message.chat.id,
                f"Найдено {len(search_results)} историй запросов:",
                reply_markup=exact_history_list(search_results),
            )
        else:
            bot.send_message(
                message.chat.id,
                "К сожалению история запросов не найдена"
                "Введите /start чтобы начать поиск гостиниц",
            )


@bot.message_handler(commands=["lowprice", "guest_rating", "bestdeal"])
def get_search_order(message: Message):
    if "lowprice" in message.text:
        order = "price"
    elif "guest_rating" in message.text:
        order = "popularity"
    else:
        order = "distance"
    update(db, User, User.chat_id == message.chat.id, {"action": 1, "order": order})
    bot.send_message(message.chat.id, "Введите город поиска:")


@bot.message_handler(content_types=["text"])
def send_buttons(message: Message):
    user = User.get(User.chat_id == message.chat.id)
    action = user.action  # ПОЛУЧАЕТ ACTION по id
    if action == 1:
        city = message.text
        cities = get_location_ids(city)
        if not cities:
            bot.send_message(
                message.chat.id,
                f"Локаций по запросу {city} не найдено, попробуйте еще раз",
            )
            return
        bot.send_message(
            message.chat.id,
            f"Вы выбрали город: {city}. Уточните локацию пожалуйста:",
            reply_markup=exact_location_keygen(cities),
        )
        update(db, User, User.chat_id == message.chat.id, {"action": 2})
    elif action == 5:
        try:
            min_price, max_price = map(int, message.text.split("-"))
            if min_price > max_price:
                bot.send_message(
                    message.chat.id, "Пожалуйста, введите цены в правильном порядке."
                )
                return

        except ValueError:
            bot.send_message(
                message.chat.id,
                "Введенные данные не являются диапазоном цен. Пожалуйста, введите цены в формате *цена_от-*цена_до"
                "Пример 0-500"
            )
            return

        bot.send_message(message.chat.id, "Введите количество человек в группе:")
        update(
            db,
            User,
            User.chat_id == message.chat.id,
            {"action": 6, "min_price": min_price, "max_price": max_price},
        )  # изменяет action в БД
    elif action == 6:
        try:
            person_count = int(message.text)
            if person_count <= 0:
                bot.send_message(
                    message.chat.id,
                    "Неверный ввод. Введите положительное число для количества человек в группе:",
                )
                return
            update(
                db,
                User,
                User.chat_id == message.chat.id,
                {"person_count": int(message.text)},
            )
        except ValueError:
            bot.send_message(
                message.chat.id,
                "Неверный ввод. Введите число для количества человек в группе:",
            )
            return

        bot.send_message(message.chat.id, "Подождите! Идет поиск гостиниц.....")
        try:
            hotels = get_hotels(
                user.destination_id,
                user.date_in,
                user.date_out,
                user.person_count,
                (user.min_price, user.max_price),
                user.order,
            )
        except requests.exceptions.ReadTimeout:
            bot.send_message(
                message.chat.id,
                "Произошла ошибка (Прошел лимит времени на запрос), повторяю запрос",
            )
            hotels = get_hotels(
                user.destination_id,
                user.date_in,
                user.date_out,
                user.person_count,
                (user.min_price, user.max_price),
                user.order,
            )
        if not hotels:
            bot.send_message(
                message.chat.id,
                "Не найдены гостиницы, введите /start, чтобы начать поиск заново",
            )
            return
        db_write(
            db,
            History,
            {"user_id": user, "event": "hotels", "search_result": json.dumps(hotels)},
        )
        hotel = hotels[0]
        photos = hotel["photos"]
        checkin = datetime.datetime.strptime(hotel['checkin'], "%Y-%m-%d").strftime("%d.%m.%Y")
        checkout = datetime.datetime.strptime(hotel['checkout'], "%Y-%m-%d").strftime("%d.%m.%Y")
        keyboard = hotel_card_keygen(hotels, photos, hotel["url"])
        bot.send_photo(
            message.chat.id,
            photo=hotel["photos"][0],
            caption=f"Название отеля: {hotel['title']}\n"
            f"Адрес: {hotel['address']}\n"
            f"Описание: {hotel['description'][:600]}\n"
            f"Цена: {hotel['price']}$ с {checkin} по {checkout}\n"
            f"Коодринаты: {hotel['coordinates'][0], hotel['coordinates'][1]}",
            reply_markup=keyboard,  # Генерирует карточки отелей согласно вашему запросу
        )
    else:
        bot.send_message(
            message.chat.id,
            "К сожалению данной команды не существует! \n"
            "Воспользуйтесь командой /help , чтобы продолжить",
        )


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    user = User.get(User.chat_id == call.message.chat.id)
    action = user.action
    date_limit = datetime.date.today()
    if call.data.startswith("loc"):
        city_id = call.data.replace("loc", "")
        update(
            db,
            User,
            User.chat_id == call.message.chat.id,
            {"action": 3, "destination_id": city_id},
        )
        user = User.get(User.chat_id == call.message.chat.id)
        calendar, step = DetailedTelegramCalendar(
            calendar_id=action + 1,
            locale="ru",
            min_date=date_limit,
            max_date=date_limit + datetime.timedelta(days=365 * 2),
        ).build()
        bot.send_message(
            call.message.chat.id,
            f"Выберите дату заезда: {LSTEP[step]}",
            reply_markup=calendar,
        )
    if call.data.startswith("cbcal"):
        if action == 3:
            result, key, step = DetailedTelegramCalendar(
                calendar_id=action,
                locale="ru",
                min_date=date_limit,
                max_date=date_limit + datetime.timedelta(days=365 * 2),
            ).process(call.data)
            if not result and key:
                bot.edit_message_text(
                    f"Выберите {LSTEP[step]}",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=key,
                )
            elif result:
                date = result.strftime("%d.%m.%Y")
                bot.send_message(
                    call.message.chat.id,
                    f"Вы выбрали дату заезда: {date}",
                )
                update(
                    db,
                    User,
                    User.chat_id == call.message.chat.id,
                    {"action": 4, "date_in": result},
                )
                calendar, step = DetailedTelegramCalendar(
                    calendar_id=action + 1,
                    locale="ru",
                    min_date=date_limit + datetime.timedelta(days=1),
                    max_date=date_limit + datetime.timedelta(days=365 * 2),
                ).build()
                bot.send_message(
                    call.message.chat.id,
                    f"Выберите дату выезда: {LSTEP[step]}",
                    reply_markup=calendar,
                )
        else:
            result, key, step = DetailedTelegramCalendar(
                calendar_id=action,
                locale="ru",
                min_date=date_limit + datetime.timedelta(days=1),
                max_date=date_limit + datetime.timedelta(days=365 * 2),
            ).process(call.data)
            if not result and key:
                bot.edit_message_text(
                    f"Выберите {LSTEP[step]}",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=key,
                )
            elif result:
                date = result.strftime("%d.%m.%Y")
                bot.send_message(
                    call.message.chat.id,
                    f"Вы выбрали дату выезда: {date}",
                )
                if user.date_in < result:
                    update(
                        db,
                        User,
                        User.chat_id == call.message.chat.id,
                        {"action": 5, "date_out": result},
                    )
                    bot.send_message(
                        call.message.chat.id,
                        "Введите диапазон цен в формате *цена_от-*цена_до (Пример: 0-500)\n"
                        "Внимение!!! Данные диапозон учитывается на период выбранных вами дат"
                    )
                else:
                    bot.send_message(
                        call.message.chat.id,
                        "Неверно выбраны даты бронирования и выезда.",
                    )
                    update(
                        db,
                        User,
                        User.chat_id == call.message.chat.id,
                        {"action": 3},
                    )
                    user = User.get(User.chat_id == call.message.chat.id)
                    calendar, step = DetailedTelegramCalendar(
                        calendar_id=user.action,
                        locale="ru",
                        min_date=date_limit,
                        max_date=date_limit + datetime.timedelta(days=365 * 2),
                    ).build()
                    bot.send_message(
                        call.message.chat.id,
                        f"Выберите дату заезда: {LSTEP[step]}",
                        reply_markup=calendar,
                    )
    if call.data.startswith("card"):
        user = User.get(User.chat_id == call.message.chat.id)
        history = (
            History.select()
            .where((History.user_id == user.id) & (History.event == "hotels"))
            .order_by(History.id.desc())
            .get()
        )
        hotels = json.loads(history.search_result)
        number = int(call.data.replace("card", ""))
        hotel = hotels[number]
        photos = hotel["photos"]
        checkin = datetime.datetime.strptime(hotel['checkin'], "%Y-%m-%d").strftime("%d.%m.%Y")
        checkout = datetime.datetime.strptime(hotel['checkout'], "%Y-%m-%d").strftime("%d.%m.%Y")
        keyboard = hotel_card_keygen(hotels, photos, hotel["url"], number)
        bot.edit_message_media(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            media=InputMediaPhoto(hotel["photos"][0]),
        )
        bot.edit_message_caption(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            caption=f"Название отеля: {hotel['title']}\n"
            f"Адрес: {hotel['address']}\n"
            f"Описание: {hotel['description'][0:600]}\n"
            f"Цена: {hotel['price']}$ с {checkin} по {checkout}\n"
            f"Координаты: {hotel['coordinates'][0], hotel['coordinates'][1]}",
            reply_markup=keyboard,
        )
    if call.data.startswith("photo"):
        user = User.get(User.chat_id == call.message.chat.id)
        history = (
            History.select()
            .where((History.user_id == user.id) & (History.event == "hotels"))
            .order_by(History.id.desc())
            .get()
        )
        hotels = json.loads(history.search_result)
        numbers = call.data.replace("photo", "")
        photo_number, hotel_number = [int(number) for number in numbers.split("_")]
        hotel = hotels[hotel_number]
        photos = hotel["photos"]
        keyboard = hotel_card_keygen(
            hotels, photos, hotel["url"], hotel_number, photo_number
        )
        bot.edit_message_media(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            media=InputMediaPhoto(hotel["photos"][photo_number]),
        )
        bot.edit_message_caption(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            caption=call.message.caption,
            reply_markup=keyboard,
        )
    if call.data.startswith("his"):
        id = call.data.replace("his", "")
        query = History.get(History.id == id)
        hotels = json.loads(query.search_result)
        hotel = hotels[0]
        photos = hotel["photos"]
        checkin = datetime.datetime.strptime(hotel['checkin'], "%Y-%m-%d").strftime("%d.%m.%Y")
        checkout = datetime.datetime.strptime(hotel['checkout'], "%Y-%m-%d").strftime("%d.%m.%Y")
        keyboard = hotel_card_keygen(hotels, photos, hotel["url"])
        bot.send_photo(
            call.message.chat.id,
            photo=hotel["photos"][0],
            caption=f"Название отеля: {hotel['title']}\n"
            f"Адрес: {hotel['address']}\n"
            f"Описание: {hotel['description'][:600]}\n"
            f"Цена: {hotel['price']}$ с {checkin} по {checkout}\n"
            f"Коодринаты: {hotel['coordinates'][0], hotel['coordinates'][1]}",
            reply_markup=keyboard,  # Генерирует карточки отелей согласно вашему запросу
        )
