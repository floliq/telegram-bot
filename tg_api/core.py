from tg_api.common.bot_init import bot
from bot_api.core import *

flag = "debug"


@bot.message_handler(commands=["start", "help"])
def send_welcome(message: Message):
    global flag
    """
    /start and /help bot commands
    :param message:
    :return:
    """
    # if not check_user_in_db(message):
    #     add_user_to_db(message)
    if "start" in message.text:
        bot.send_message(
            message.chat.id,
            "Приветствую в боте по поиску отелей. Для начала введите, пожалуйста, город поиска ниже:",
        )
        flag = "enter_city"


@bot.message_handler(content_types=["text"])
def send_buttons(message: Message):
    global flag
    if flag == "enter_city":
        city = message.text
        bot.send_message(
            message.chat.id,
            f"Вы выбрали город: {city}. Уточните локацию пожалуйста:",
            reply_markup=exact_location_keygen(city),
        )

    #     history_log(message, '/start', '')
    # else:
    #     bot.send_message(message.chat.id, translate('help', message))
    #     history_log(message, '/help', '')


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
