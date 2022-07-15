from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram import types, Dispatcher
from createBot import dp
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from datetime import datetime, timedelta
from pythonping import ping

import uuid

import validators
from validators import ValidationFailure

import urllib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Проверка правильности ссылок
def is_string_an_url(url_string: str) ->bool:
    result = validators.url(url_string)
    if isinstance(result, ValidationFailure):
        return False
    return result

# Класс FSMstate для диалога с пользователем
class FSMadd(StatesGroup):
    site = State()
    answer = State()

# Классы для заполнения БД
class users_db():
    tg_user_id = str()
    UID_user = str()

class sites_db():
    id = str()
    site_url = str()
    status = str()
    ping = str()
    check_date = str()

# Запуск класса
async def cm_start(message : types.Message):
    await FSMadd.site.set()
    await message.reply('Введите адрес сайта (Пример: google.com)')

# Выход из состояний
async def cancel_handler(message: types.Message, state: FSMContext):
        if message.text.strip() == "отмена" or "Отмена":
            current_state = await state.get_state()
            if current_state is None:
                await message.answer('Вам нечего отменять =)')
                await message.delete()
                return
            await state.finish()
            await message.reply('Вы вернулись в главное меню')

# Фиксируем ответ (адрес сайта)
async def load_url(message: types.Message, state: FSMadd):
    url = str("http://" + message.text) #
    if (is_string_an_url(url.strip()) == True):
        async with state.proxy() as data:
          data['site'] = message.text
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as err:
            er = str(err.code)
            await message.reply("Сервер не смог выполнить запрос по данному адресу")
            await message.answer("Код ошибки: " + er)
        except URLError as err:
            await message.reply("Не удалось получить доступ к сайту")
            e = str(err.reason)
            await message.answer("Код ошибки: " + e)
            await message.answer("Добавить его в список мониторинга? (ДА/НЕТ)")
            sites_db.site_url = message.text
            sites_db.status = "Offline"
            sites_db.ping = "None"
            await FSMadd.next()
        else:
            await message.reply("Сайт работает!")
            ping_only = ping(message.text, size=1, count=1)
            ping_only = str(ping_only.rtt_avg_ms) + " ms"
            sites_db.ping = ping_only
            await message.answer("Время отклика: " + ping_only)
            await message.answer("Добавить его в список мониторинга? (ДА/НЕТ)")
            sites_db.site_url = message.text
            sites_db.status = "Online"
            await FSMadd.next()
    else:
        await message.reply("Неправильно введен URL, повторите попытку (Пример: google.com)")

# Фиксируем ответ (ДА/НЕТ)
async def load_answer(message: types.Message, state: FSMContext):
    if (message.text.strip() == "ДА"):
        async with state.proxy() as data:
            data['answer'] = message.text
        test = list()
        test = sqlite_db.sql_read_user(message.from_user.id)
        amount = len(test)
        if (amount < 10):
            users_db.tg_user_id = str(message.from_user.id)
            users_db.UID_user = str(uuid.uuid4())

            sites_db.id = str(uuid.uuid4())
            sites_db.check_date = datetime.now()
            #print(datetime.today())
            #f = datetime.strptime(sqlite_db.sql_get_last_date(sites_db.id), "%Y-%m-%d %H:%M:%S.%f")
            #print(sqlite_db.sql_get_last_date(sites_db.id))
            #print(datetime.strptime(sqlite_db.sql_get_last_date(sites_db.id), "%Y-%m-%d %H:%M:%S.%f"))
            #print(datetime.today() - f)
            #print(str(datetime.today() - sqlite_db.sql_get_last_date(sites_db.id)))

            await sqlite_db.sql_add_user()
            await sqlite_db.sql_add_site()
            #await sqlite_db.sql_add_sitelog()
            await sqlite_db.sql_add_conns()
            await state.finish()
            await message.answer("Сайт добавлен в список мониторинга")
        else:
            await message.answer("Вы уже добавили 10 сайтов в список мониторинга")
            await message.answer("Чтобы добавить этот сайт, нужно убрать один из списка")
            await state.finish()
    elif (message.text.strip() == "НЕТ"):
        #sites_db.id = str(uuid.uuid4())
        #sites_db.check_date = datetime.now()
        #await sqlite_db.sql_add_sitelog()
        await message.reply("Хорошо, не добавляю сайт в список мониторинга")
        await state.finish()
    else:
        await message.reply("Неправильный ответ, повторите попытку")

def register_handlers_addSite(dp:Dispatcher):
    dp.register_message_handler(cm_start, commands=['Добавить'], state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена' or 'Отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_url, content_types=['text'], state=FSMadd.site)
    dp.register_message_handler(load_answer, state=FSMadd.answer)
