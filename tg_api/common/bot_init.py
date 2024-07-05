import telebot
from config.config import Settings

bot_settings = Settings()

bot = telebot.TeleBot(bot_settings.bot_token.get_secret_value(), parse_mode="HTML")
