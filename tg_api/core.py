from database.common.models import db, User, History
from tg_api.common.bot_init import bot
from bot_api.core import *
from database.core import crud

db_write = crud.create()
db_read = crud.retrieve()
check_exists_data = crud.check_exists()
update = crud.update_row()
# get_action = crud.retrieve_row()


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
        update(db, User, User.chat_id == message.chat.id, {"action": 1})  #если есть id - INSERT, нет - UPDATE
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
        bot.send_message(
            message.chat.id,
            f"Вы выбрали город: {city}. Уточните локацию пожалуйста:",
            reply_markup=exact_location_keygen(city),
        )
        update(db, User, User.chat_id == message.chat.id, {"action": 2})  # изменяет action в БД
    elif action == 3:
        date_in = message.text
        bot.send_message(
            message.chat.id,
            f"Вы выбрали дату заезда: {date_in}. Выберите дату выезда:"
        )
        update(db, User, User.chat_id == message.chat.id, {"action": 4})  # изменяет action в БД
    elif action == 4:
        date_out = message.text
        bot.send_message(
            message.chat.id,
            "Введите диапазон цен в формате *цена от-*цена до",
        )
        update(db, User, User.chat_id == message.chat.id, {"action": 5})  # изменяет action в БД
    elif action == 5:
        min_price, max_price = map(int, message.text.split("-"))
        bot.send_message(
            message.chat.id,
            "Введите количество человек в группе:"
            )
        update(db, User, User.chat_id == message.chat.id, {"action": 6})  # изменяет action в БД
    elif action == 6:
        city_id = user.destination_id
        # data = get_hotels(-553173) # берет отели и его цены
        # print(get_all_hotel_info(77634, data)) передаем id и цены, получаем всю  инфу
        hotels = get_hotels(city_id)
        list_of_data = [get_all_hotel_info(hotel_id) for hotel_id in hotels]
        first_hotel = list_of_data[0]
        print(first_hotel)
        # bot.send_photo(
        #     message.chat.id,
        #     "",
        #     # "Список предложенных отелей согласно вашему запросу:",
        #     reply_markup=hotel_card_keygen(list_of_data, 0),  # Генерирует карточки отелей согласно вашему запросу
        # )

    # elif action == 6:


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data.startswith("loc"):
        city_id = call.data.replace("log", '')
        update(db, User, User.chat_id == call.message.chat.id, {"action": 3, "destination_id": city_id})
        bot.send_message(call.message.chat.id, "Введите желаемую дату заезда: ")
        # bot.send_message(
        #     call.message.chat.id,
        #     f"Отели в выбранном городе:",
        #     reply_markup=hotel_card_keygen(city_id),
        # )
