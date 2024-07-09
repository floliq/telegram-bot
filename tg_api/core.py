
from database.common.models import db, User, History
from tg_api.common.bot_init import bot
from bot_api.core import *
from database.core import crud

db_write = crud.create()
db_read = crud.retrieve()
check_exists_data = crud.check_exists()
update_action = crud.update_row()
get_action = crud.retrieve_row()


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
        update_action(db, User, User.chat_id == message.chat.id, {"action": 1}) #если есть id - INSERT, нет - UPDATE
    if "start" in message.text:
        bot.send_message(
            message.chat.id,
            "Приветствую в боте по поиску отелей. Для начала введите, пожалуйста, город поиска ниже:",
        )


@bot.message_handler(content_types=["text"])
def send_buttons(message: Message):
    user = User.get(message.chat.id == User.chat_id)
    action = user.action # ПОЛУЧАЕТ ACTION по id
    if action == 1:
        city = message.text
        bot.send_message(
            message.chat.id,
            f"Вы выбрали город: {city}. Уточните локацию пожалуйста:",
            reply_markup=exact_location_keygen(city),
        )


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data[:3] == "loc":
        city_id = call.data[3:]
        print(city_id)
        bot.send_message(
            call.message.chat.id,
            f"Отели в выбранном городе:",
            reply_markup=hotel_card_keygen(city_id),
        )
