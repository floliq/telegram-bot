# Телеграм бот @Helper_Hotels_From_Booking_bot

Бот для поиска гостиниц с использованием API Booking.com

## Особенности

Данный бот позволяет:
* подбирать отели по самой низкой или рекомендуемой цене;
* подбирать отели по близкие к центру города;  
* задавать диапазон цен.

## Требования
Обязательно установаить Python 3.10 или выше

## Установка 
- Склонировать репозиторий и перейти в папку
```cmd
git clone https://gitlab.skillbox.ru/vladislav_boiko_2/python_basic_diploma.git
cd .\python_basic_diploma\
```
- Создать и запустить виртуальное окружение
```cmd
python -m venv .venv
.\.venv\Scripts\activate
```
- Установаить все пакеты из файла requirements.txt
```cmd
pip install -r requirements.txt
```
- Получить API_KEY на [сайте](https://rapidapi.com/tipsters/api/booking-com)
- Получить BOT_TOKEN у [Bot Father](https://telegram.me/BotFather)
- Создать файл .env и настроить по образцу
```.env
API_KEY = 'ВАШ КЛЮЧ К API BOOKING.COM'  
BOT_TOKEN = 'ВАШ КЛЮЧ К ТГ БОТУ'
HOST_API = 'booking-com.p.rapidapi.com'
```
- Запустить приложение
```cmd
python .\main.py
```
После выполнения всех инструкций в консоли должна вывестись READY
