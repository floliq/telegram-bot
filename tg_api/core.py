import telebot
from api.core import api, url, headers
from tg_api.common.bot_init import bot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

flag = "debug"


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    global flag
    """
    /start and /help bot commands
    :param message:
    :return:
    """
    # if not check_user_in_db(message):
    #     add_user_to_db(message)
    if 'start' in message.text:
        bot.send_message(message.chat.id,
                         "Приветствую в боте по поиску отелей. Для начала введите, пожалуйста, город поиска ниже:")
        flag = "enter_city"


def exact_location_keygen(city):
    keyboard = InlineKeyboardMarkup(row_width=2)
    find_city = api.get_location()
    params = {"name": city, "locale": "en-gb"}
    response = find_city("GET", url, headers, params, 5).json()
    for location in response:
        keyboard.add(InlineKeyboardButton(text=location["label"], callback_data=f"loc{location["dest_id"]}"))

    # for lat, lng, name in get_nearest_hotels(location):
    #     keyboard.add(InlineKeyboardButton(text=name, callback_data=exact_location_keygen(f"{lat},{lng}")))
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return keyboard


def hotel_card_keygen(dest_id):
    find_hotels = api.get_best_hotel()
    params = {
        "checkout_date": "2024-09-15",
        "order_by": "popularity",
        "filter_by_currency": "AED",
        "include_adjacency": "true",
        "categories_filter_ids": "class::2,class::4,free_cancellation::1",
        "room_number": "1",
        "dest_id": dest_id,
        "dest_type": "city",
        "adults_number": "2",
        "page_number": "0",
        "checkin_date": "2024-09-14",
        "locale": "en-gb",
        "units": "metric",
    }
    response = find_hotels(
        "GET",
        url,
        headers,
        params,
        5
    )
    response = response.json()
    print(response)
    keyboard = InlineKeyboardMarkup()

    # hotel['hotel_name_trans']
    # hotel['url']
    # hotel['price_min']
    # hotel['price_max']
    # hotel['rating']
    # hotel['rating_count']
    # hotel['distance']
    # hotel['star_rating']
    # hotel['hotel_id']
    # hotel['image_url']
    # hotel['hotel_name_trans']
    # hotel['is_free_cancellation']
    # hotel['is_direct_booking']
    # hotel['is_superior']
    # hotel['is_premium']
    # hotel['is_luxury']
    # hotel['is_superior_luxury']
    # hotel['is_family']
    # hotel['is_superior_family']
    # hotel['is_premium_family']
    # hotel['is_luxury_family']
    # hotel['is_superior_luxury_family']
    # hotel['is_hotel_club']

    for hotel in response["result"]:
        keyboard.add(InlineKeyboardButton(text=hotel['hotel_name_trans'], callback_data="hotel"))

    return keyboard


@bot.message_handler(content_types=['text'])
def send_buttons(message: Message):
    global flag
    if flag == "enter_city":
        city = message.text
        bot.send_message(message.chat.id, f"Вы выбрали город: {city}. Уточните локацию пожалуйста:",
                         reply_markup=exact_location_keygen(city))

    #     history_log(message, '/start', '')
    # else:
    #     bot.send_message(message.chat.id, translate('help', message))
    #     history_log(message, '/help', '')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data[:3] == "loc":
        city_id = call.data[3:]
        print(city_id)
        bot.send_message(call.message.chat.id, f"Отели в выбранном городе:", reply_markup=hotel_card_keygen(city_id))


print("Ready")
bot.infinity_polling()
