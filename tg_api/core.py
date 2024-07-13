import json

from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime

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
        db_write(db, User, {"chat_id": message.chat.id, "action": 1})
    else:
        update(
            db, User, User.chat_id == message.chat.id, {"action": 1}
        )  # если есть id - INSERT, нет - UPDATE
    if "start" in message.text:
        bot.send_message(
            message.chat.id,
            "Приветствую в боте по поиску отелей. Для начала введите, пожалуйста, город поиска ниже:",
        )


@bot.message_handler(content_types=["text"])
def send_buttons(message: Message):
    user = User.get(User.chat_id == message.chat.id)
    action = user.action  # ПОЛУЧАЕТ ACTION по id
    if action == 1:
        city = message.text
        cities = get_location_ides(city)
        if not cities:
            bot.send_message(
                message.chat.id,
                f"Локаций по запросу {city} не найдено, введите город еще раз",
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
        bot.send_message(message.chat.id, "Подождите! Идет поиск гостиниц.....")
        city_id = user.destination_id
        hotels = get_hotels(city_id)
        db_write(db, History, {"user_id": user, "event": "hotels", "search_result": json.dumps(hotels)})
        hotel = hotels[0]
        # for hotel in hotels:
        #     print(hotel)
        # print(first_hotel)
        keyboard = hotel_card_keygen(hotels, 0)
        bot.send_photo(
            message.chat.id,
            photo=hotel["photo"],
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
            calendar_id= action + 1,
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
        history = History.select().where((History.user_id == user.id) & (History.event == "hotels")).order_by(History.id.desc()).get()
        print(history.id)
        hotels = json.loads(history.search_result)
        number = int(call.data.replace("card", ""))
        hotel = hotels[number]
        keyboard = hotel_card_keygen(hotels, number)
        bot.edit_message_media(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            media=types.InputMediaPhoto(hotel["photo"]),
        )
        bot.edit_message_caption(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            caption=f"Название отеля: {hotel['title']}\n"
            f"Ссылка на бронирование: {hotel['url']}\n"
            f"Описание: {hotel['description'][0:150]}\n"
            f"Цена: {hotel['price']} $\n"
            f"Выбранные даты - въезд: {user.date_in}, выезд: {user.date_out}\n"
            f"Коодринаты: {hotel['coordinates'][0], hotel['coordinates'][1]}",
            reply_markup=keyboard,
        )
