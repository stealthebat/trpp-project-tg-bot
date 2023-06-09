import requests
import datetime
from pprint import pprint
import io
import matplotlib.pyplot as plt
from telegram import InputFile
from aiogram.types import InputFile
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply(f"Приветствую Вас, {message.from_user.username}!\n"
                        "Этот бот может помочь вам узнать погоду в определённом городе или стране.\n"
                        "Вы можете написать /help, чтобы просмотреть доступные команды.")


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.reply("Для получения прогноза погоды введите название города или страны.\n"
                        "/start - отобразить приветствие\n"
                        "/get_temperature_graph - получить график температуры для указанного города или страны\n")


@dp.message_handler(commands=["get_temperature_graph"])
async def get_temperature_graph_command(message: types.Message):
    try:
        city = ' '.join(message.text.split()[1:])
        url = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}'
                           f'&units=metric&lang=ru')
        data = url.json()
        pprint(data)

        temps = [forecast['main']['temp'] for forecast in data['list'][:9]]
        time_intervals = [datetime.datetime.strptime(forecast['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%m-%d %H:%M')
                          for forecast in data['list'][:9]]

        fig, ax = plt.subplots(figsize=(8, 10))
        ax.plot(time_intervals, temps, color='red', linewidth=2)
        ax.legend(['Temperature'])
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.set_title(f'{city}. Температура каждые 3 часа в сутки', fontsize=16)
        ax.set_xlabel('Время', fontsize=12)
        ax.set_ylabel('Температура в градусах Цельсия', fontsize=12)
        ax.set_xlim([min(time_intervals), max(time_intervals)])
        ax.set_facecolor('whitesmoke')
        ax.tick_params(axis='both', which='major', labelsize=10)
        plt.xticks(rotation=35)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        buf.name = f"{city}_temperature.png"

        await bot.send_photo(message.chat.id, InputFile(buf))

    except:
        await message.reply("\U00002620 Проверьте правильность записи названия города или страны \U00002620")


@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        url = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units"
            f"=metric&lang=ru")
        data = url.json()
        pprint(data)

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Иконку погоды не удалось определить"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        await message.reply(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                            f"Локация: {city}\nТемпература: {cur_weather} C°\n"
                            f"{wd}\n"
                            f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n"
                            f"Продолжительность дня: {length_of_the_day}\n\n"
                            f"Хорошего Вам дня!")

    except:
        await message.reply("\U00002620 Проверьте правильность записи названия города или страны \U00002620")


if __name__ == "__main__":
    executor.start_polling(dp)
