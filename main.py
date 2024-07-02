from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import requests
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter
from config import config

def gen_markup():
    # Создаём объекты кнопок.
    button_1 = KeyboardButton(text="Собаки 🦮")
    button_2 = KeyboardButton(text="Кошки 🐈")

    # Создаём объект клавиатуры, добавляя в него кнопки.
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(button_1, button_2)
    return keyboard

def get_popular_attraction_near_by():
    response = requests.get('https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query=man', 
                        headers={'accept': 'application/json',
                                 'x-rapidapi-key': '792a15e231msh2f2c7dd58b094ebp112b6djsnb64176107d46'})
    # response = requests.get(f'https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query=man', params={
    #     'key': 'x-rapidapi-key',
    #     'value': '792a15e231msh2f2c7dd58b094ebp112b6djsnb64176107d46'
    # })
    print(response.json())
    return response

bot = telebot.TeleBot(config.BOT_TOKEN)
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.send_message(
        message.from_user.id,
        "Какое животное тебе нравится больше?",
        reply_markup=gen_markup(),  # Отправляем клавиатуру.
    )

@bot.message_handler(commands=["get"])
def get_hotel(message):
    bot.send_message(
        message.from_user.id,
        get_popular_attraction_near_by()
    )

@bot.message_handler(func=lambda message: message.text == "Собаки 🦮")
def dog_answer(message):
    bot.send_message(
        message.from_user.id,
         "Я тоже люблю собак, они так мило машут хвостиком!",
        reply_markup=ReplyKeyboardRemove(),  # Удаляем клавиатуру.
    )

@bot.message_handler(func=lambda message: message.text == "Кошки 🐈")
def cat_answer(message):
    bot.send_message(
        message.from_user.id,
        "Я тоже люблю кошек, они так умилительно мурлыкают!",
        reply_markup=ReplyKeyboardRemove(),  # Удаляем клавиатуру.
    )


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)

if __name__ == "__main__":
    bot.infinity_polling()