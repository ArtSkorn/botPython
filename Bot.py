#Основной бот проект. до 30 ноября

from telebot import TeleBot, types
from datetime import datetime
import threading
import time
import pandas
import requests
from urllib.parse import quote_plus
import test2
import random

BOTTOKEN = "8550559112:AAE9DbKrlTMxrwWWXzRCLWr7UdxWjN8OJqY"
bot = TeleBot(BOTTOKEN) #связь с ботом

users = set()

@bot.message_handler(commands=['start'])
def sf(m):
    #Бот высылает приветсвенный стикер
    bot.send_sticker(m.chat.id, "CAACAgIAAxkBAAEPwBdpEqiSxlRd_H20g8brjTsUU9nWFAACBQADwDZPE_lqX5qCa011NgQ")
    bot.send_message(m.chat.id, "Приветсвую. Это бот Колева Сергея")


@bot.message_handler(commands=['info'])
def info(m):
    klava1 = types.InlineKeyboardMarkup()
    klava2 = types.ReplyKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("/notice", callback_data="notice")
    btn2 = types.InlineKeyboardButton("/unsub", callback_data="unsub")
    btn3 = types.InlineKeyboardButton("/image", callback_data="image")
    btn4 = types.InlineKeyboardButton("/parser", callback_data="parser")

    btn5 = types.KeyboardButton("/notice")
    btn6 = types.KeyboardButton("/unsub")
    btn7 = types.KeyboardButton("/image")
    btn8 = types.KeyboardButton("/parser")

    klava1.add(btn1, btn2, btn3, btn4)
    klava2.add(btn5, btn6, btn7, btn8)
    #потом добавить расписание и расписание на сегодня
    bot.send_message(m.chat.id, "Список команд бота:\n"
                                "/start - приветсвтие\n"
                                "/info - все команды бота\n"
                                "/notice - подписаться на уведомления\n"
                                "/unsub - отписаться от уведомлений\n"
                                "/image - сгенерировать картинку по текстовому запросу\n"
                                "/parser - получить подборку товаров электроники по запросу", reply_markup=klava1)

    bot.send_message(m.chat.id,"Reply кнопки подключены ✅", reply_markup=klava2)

    @bot.message_handler(commands=['notice'])
    def noticeCMD(m):
        users.add(m.chat.id)
        bot.send_message(m.chat.id, "Вы подписались на уведомления")

    @bot.message_handler(commands=['unsub'])
    def unsubCMD(m):
        users.discard(m.chat.id)
        bot.send_message(m.chat.id, "Вы отписались от уведомлений")

    @bot.message_handler(commands=['image'])
    def imgCMD(m):
        # ------------ГЕНЕРАТОР ИЗОБРАЖЕНИЙ --------

        @bot.message_handler(commands=['image'])
        def sendImg(m):
            prompt = m.text.partition(' ')[2].strip()  # чисты запрос после пробела
            bot.send_message(m.chat.id, "Ищу...")
            # генерим рандомное число
            seed = random.randint(0, 2_000_000_000)
            # улучшение запроса
            q = quote_plus(f"{prompt}, high quality, very detailed, soft light")
            url = f"https://image.pollinations.ai/prompt/{q}?width=500&height=500&seed={seed}&n=1"
            res = requests.get(url, timeout=90, allow_redirects=True)
            bot.send_photo(m.chat.id, res.content)
        # --------------------------------------

    @bot.message_handler(commands=['parser'])
    def parceCMD(m):
        # -----------ПАРС с САЙТА ДНС-----------------
        @bot.message_handler(commands=['parser'])
        def parser(m):
            prompt = m.text.partition(' ')[2].strip()
            result = test2.dns_search_uc(prompt)
            bot.send_message(m.chat.id, result)
        # ------------------------------------------

# ПОТОКИ --------------------------------------------------

def get_beautiful_column_name(column: str) -> str:

    """Преобразует названия колонок в красивые"""

    column_names = {
        'Time': ' Время',
        'Subject': ' Предмет',
        'Teacher': ' Преподаватель',
        'Room': ' Аудитория',
    }
    return column_names.get(column, column)

days_of_week = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье"
}

def setShedule(user):
    today_weekday = datetime.today().weekday() + 1  # 1–7

    # Суббота

    if today_weekday == 6:
        bot.send_message(
            user,
            " *Суббота* - занятий нет!\nМожно отдохнуть! ",
            parse_mode='Markdown'
        )
        return

    # Воскресенье

    if today_weekday == 7:
        bot.send_message(
            user,
            " *Воскресенье* - занятий нет!\nИдеальный день для отдыха! ",
            parse_mode='Markdown'
        )
        return

    df = pandas.read_excel('schedule.xlsx')

    today_schedule = df[df['Day'] == today_weekday]
    if today_schedule.empty:
        day_name = days_of_week.get(today_weekday, "сегодня")
        bot.send_message(
            user,
            f" *{day_name.upper()}* - занятий нет!\nОтличный день для саморазвития! ",
            parse_mode='Markdown'
        )
        return
    day_name = days_of_week.get(today_weekday, "сегодня")
    response = f" *РАСПИСАНИЕ НА {day_name.upper()}* \n\n"
    for _, row in today_schedule.iterrows():
        response += "" * 20 + "\n"
        for column, value in row.items():
            if column != 'Day' and pandas.notna(value) and str(value).strip() != '':
                column_name = get_beautiful_column_name(column)
                response += f"*{column_name}:* {value}\n"
        response += "\n" + "═" * 30 + "\n\n"
    total_lessons = len(today_schedule)
    response += f" *Всего пар: {total_lessons}*"
    bot.send_message(user, response, parse_mode='Markdown')

def check_time():
    while True:
        now = datetime.now()
        if now.hour == 19 and now.minute == 47:
            print("lslsl")
            for user in list(users):
                setShedule(user)
        time.sleep(1)

#запускает фоновый поток
def notification():
    scheduler_thread = threading.Thread(target=check_time)
    scheduler_thread.daemon = True  # фоновый поток
    scheduler_thread.start()


#если скрипт запущен
if __name__ == "__main__":
    print("Бот запущен...")
    notification()              # Запуск фоновых уведомлений
    bot.infinity_polling()    # Основной цикл бота




