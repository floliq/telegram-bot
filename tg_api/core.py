import json

from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime

from api.core import get_location_ids, hotel_photos
from database.common.models import db, User, History
from tg_api.common.bot_init import bot
from bot_api.core import *
from database.core import crud

#description - срезы

db_write = crud.create()
db_read = crud.retrieve()
check_exists_data = crud.check_exists()
update = crud.update_row()


@bot.message_handler(commands=["start", "help"])
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
    else:
        bot.send_message(
            message.chat.id,
            "Используйте следующие команды:\n"
            "/help - получить справку\n"
            "/lowprice - отели с низкими ценами\n"
            "/guest_rating - самые популярные отели\n"
            "/bestdeal - отели ближе всего к центру\n"
            "/history - история запросов",
        )


@bot.message_handler(commands=['lowprice', 'guest_rating', 'bestdeal'])
def get_search_order(message: Message):
    if not check_exists_data(db, User, User.chat_id == message.chat.id):
        db_write(db, User, {"chat_id": message.chat.id})
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
        update(
            db, User, User.chat_id == message.chat.id, {"action": 2}
        )
    elif action == 5:
        try:
            min_price, max_price = map(int, message.text.split("-"))
            if min_price > max_price:
                bot.send_message(message.chat.id, "Пожалуйста, введите цены в правильном порядке.")
                return
        except ValueError:
            bot.send_message(
                message.chat.id,
                "Введенные данные не являются диапазоном цен. Пожалуйста, введите цены в формате *цена от-*цена до",
            )
            return

        bot.send_message(message.chat.id, "Введите количество человек в группе:")
        update(
            db, User, User.chat_id == message.chat.id, {"action": 6}
        )  # изменяет action в БД
    elif action == 6:
        try:
            person_count = int(message.text)
            if person_count <= 0:
                bot.send_message(message.chat.id,
                                 "Неверный ввод. Введите положительное число для количества человек в группе:")
                return
        except ValueError:
            bot.send_message(message.chat.id, "Неверный ввод. Введите число для количества человек в группе:")
            return

        bot.send_message(message.chat.id, "Подождите! Идет поиск гостиниц.....")
        city_id = user.destination_id
        order = user.order
        hotels = get_hotels(city_id, order)
        db_write(db, History, {"user_id": user, "event": "hotels", "search_result": json.dumps(hotels)})
        hotel = hotels[0]
        # photos = hotel_photos(hotel["id"])
        photos = hotel["photos"]
        keyboard = hotel_card_keygen(hotels, photos, 0)
        bot.send_photo(
            message.chat.id,
            photo=hotel["photos"][0],
            caption=f"Название отеля: {hotel['title']}\n"
                    f"Ссылка на бронирование: {hotel['url']}\n"
                    f"Описание: {hotel['description'][:150]}\n"
                    f"Цена: {hotel['price']}\n"
                    f"Выбранные даты - въезд: {user.date_in}, выезд: {user.date_out}\n"
                    f"Коодринаты: {hotel['coordinates'][0], hotel['coordinates'][1]}",
            reply_markup=keyboard,  # Генерирует карточки отелей согласно вашему запросу
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
        db_write(
            db,
            History,
            {"user_id": user, "event": "location", "search_result": city_id},
        )
        calendar, step = DetailedTelegramCalendar(
            calendar_id=action + 1,
            locale="ru",
            min_date=date_limit,
            max_date=date_limit + datetime.timedelta(days=365 * 2)
        ).build()
        bot.send_message(
            call.message.chat.id,
            f"Выберите дату заезда: {LSTEP[step]}",
            reply_markup=calendar,
        )
    if call.data.startswith("cbcal"):
        result, key, step = DetailedTelegramCalendar(
            calendar_id=action,
            locale="ru",
            min_date=date_limit,
            max_date=date_limit + datetime.timedelta(days=365 * 2)).process(call.data)
        if not result and key:
            bot.edit_message_text(
                f"Выберите {LSTEP[step]}",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=key,
            )
        elif result:
            if action == 3:
                bot.send_message(
                    call.message.chat.id,
                    f"Вы выбрали дату заезда: {result}",
                )
                update(
                    db, User, User.chat_id == call.message.chat.id, {"action": 4, "date_in": result}
                )
                calendar, step = DetailedTelegramCalendar(
                    calendar_id=action + 1,
                    locale="ru",
                    min_date=date_limit,
                    max_date=date_limit + datetime.timedelta(days=365 * 2)).build()
                bot.send_message(
                    call.message.chat.id,
                    f"Выберите дату выезда: {LSTEP[step]}",
                    reply_markup=calendar,
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    f"Вы выбрали дату выеза: {result}",
                )

                if (datetime.datetime.strptime(user.date_in, "%Y-%m-%d").date() < result):
                    update(
                        db, User, User.chat_id == call.message.chat.id, {"action": 5, "date_out": result}
                    )
                    bot.send_message(
                        call.message.chat.id,
                        "Введите диапазон цен в формате *цена от-*цена до",
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
                        max_date=date_limit + datetime.timedelta(days=365 * 2)
                    ).build()
                    bot.send_message(
                        call.message.chat.id,
                        f"Выберите дату заезда: {LSTEP[step]}",
                        reply_markup=calendar,
                    )
    if call.data.startswith("card"):
        user = User.get(User.chat_id == call.message.chat.id)
        history = History.select().where((History.user_id == user.id) & (History.event == "hotels")).order_by(
            History.id.desc()).get()
        hotels = json.loads(history.search_result)
        number = int(call.data.replace("card", ""))
        hotel = hotels[number]
        photos = hotel["photos"]
        keyboard = hotel_card_keygen(hotels, photos, number)
        bot.edit_message_media(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            media=types.InputMediaPhoto(hotel["photo"][0]),
        )
        bot.edit_message_caption(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            caption=f"Название отеля: {hotel['title']}\n"
                    f"Ссылка на бронирование: {hotel['url']}\n"
                    f"Описание: {hotel['description'][0:150]}\n"
                    f"Цена: {hotel['price']} $\n"
                    f"Выбранные даты - въезд: {user.date_in}, выезд: {user.date_out}\n"
                    f"Координаты: {hotel['coordinates'][0], hotel['coordinates'][1]}",
            reply_markup=keyboard,
        )
    if call.data.startswith("photo"):
        user = User.get(User.chat_id == call.message.chat.id)
        history = History.select().where((History.user_id == user.id) & (History.event == "hotels")).order_by(
            History.id.desc()).get()
        hotels = json.loads(history.search_result)
        numbers = call.data.replace("photo", "")
        photo_number, hotel_number = [int(number) for number in numbers.split("_")]
        hotel = hotels[hotel_number]
        photos = hotel["photos"]
        keyboard = hotel_card_keygen(hotels, photos, hotel_number, photo_number)
        # print(call)
        # print("\n\n\n\n")
        # print(call.message)
        bot.edit_message_media(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            media=types.InputMediaPhoto(hotel["photos"][photo_number]),
        )
        bot.edit_message_caption(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            caption=call.message.caption,
            reply_markup=keyboard
        )