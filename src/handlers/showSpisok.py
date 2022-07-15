from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram import types, Dispatcher
from createBot import dp
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
#from handlers.update import FSMUpdate
import urllib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pythonping import ping
import re
from datetime import datetime

class get_spisok_bd():
    tg_user_id = str()
    site_url = list(str())
    status = str()
    ping = str()
    check_date = str()

class number():
    number = int()

class FSMUpdate(StatesGroup):
    number = State()
    answer = State()
    site = State()

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

async def show_spisok(message: types.Message):
    
    if sqlite_db.sql_get_amount(message.from_user.id) != 0:
        await FSMUpdate.number.set()
        get_spisok_bd.tg_user_id = str(message.from_user.id)
        spisok = sqlite_db.sql_get_spisok(str(message.from_user.id))
        await message.answer("Вывожу Ваш список сайтов на мониторинг")
        for i in range(len(spisok)):
            await message.answer(str("   " + str(i+1) + ". " + str(spisok[i])))
        await message.answer("Вы можете ввести номер сайта, чтобы обновить его данные.")
    else:
        await message.answer("Вы еще не добавили ни одного сайта в список")

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

async def load_number(message : types.Message, state : FSMContext):
    if message.text.isdigit():
        if int(message.text) == 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10:
            check = int(message.text.strip())
            for_amount = list(sqlite_db.sql_read_user(message.from_user.id))
            amount = len(for_amount)
            if check <= amount:
                spisok = sqlite_db.sql_get_url(str(message.from_user.id))
                uid = sqlite_db.sql_get_uid(str(message.from_user.id))
                i = int(message.text)
                url = str(spisok[i-1]) 
                url1 = str(spisok[i-1])
                url = re.sub(r'[,\'\"\(\)]', '', url)
                url1 = re.sub(r'[,\'\"\(\)]', '', url1)
                url1 = str("http://" + url1)
                uid = str(uid[i-1])
                uid = re.sub(r'[,\'\"\(\)]', '', uid)
                req = Request(url1)
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
                    sites_db.site_url = url
                    sites_db.status = "Offline"
                    sites_db.ping = "None"
                    sites_db.check_date = datetime.now()
                    await sqlite_db.sql_update_site(sites_db.id, sites_db.status, sites_db.ping, sites_db.check_date)
                    await sqlite_db.sql_add_sitelog(sites_db.id, sites_db.status, sites_db.ping, sites_db.check_date)
                    await state.finish()
                else:
                    await message.reply("Сайт работает!")
                    ping_only = ping(url , size=1, count=1)
                    ping_only = str(ping_only.rtt_avg_ms) + " ms"
                    sites_db.ping = ping_only
                    await message.answer("Время отклика: " + ping_only)
                    sites_db.site_url = url
                    sites_db.status = "Online"
                    sites_db.check_date = datetime.now()
                    await sqlite_db.sql_update_site(sites_db.id, sites_db.status, sites_db.ping, sites_db.check_date)
                    await sqlite_db.sql_add_sitelog(sites_db.id, sites_db.status, sites_db.ping, sites_db.check_date)
                    await state.finish()
            else:
                await message.answer("Введенный номер превышает количество сайтов в списке")
        else:
            await message.answer('Неправильно введен номер, повторите попытку')
    else:
        await message.answer ('Неправильно введен номер, повторите попытку')

    
    
def register_handlers_showSpisok(dp : Dispatcher):
    dp.register_message_handler(show_spisok, commands=['Список'])
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена' or 'Отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_number, state=FSMUpdate.number)