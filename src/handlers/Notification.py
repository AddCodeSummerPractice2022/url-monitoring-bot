import re
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from createBot import dp
from data_base import sqlite_db
from aiogram.dispatcher.filters import Text
import schedule
import time
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pythonping import ping
from datetime import datetime
import asyncio
#from typing_extensions import Self

class FSMNotify(StatesGroup):
    number = State()
    freq = State()
    answer = State()

class site_info():
    number = int()
    date = str()
    uid = str()
    #id = str()
    site_url = str()
    status = str()
    ping = str()
    check_date = str()

class users_db():
    tg_user_id = str()
    UID_user = str()

#class sites_db():
#    id = str()
#    site_url = str()
#    status = str()
#    ping = str()
#    check_date = str()

async def printprogress():
    await sqlite_db.sql_update_site(site_info.uid, site_info.status, site_info.ping, site_info.check_date)

async def run():
    schedule.every(3).seconds.do(printprogress) 

    while True: 
        schedule.run_pending() 
        time.sleep(1)
    
async def cm_start(message : types.Message):
    await FSMNotify.number.set()
    spisok = sqlite_db.sql_get_spisok(str(message.from_user.id))
    await message.answer("Вывожу Ваш список сайтов для настройки уведомлений")
    for i in range(len(spisok)):
        await message.answer(str("   " + str(i+1) + ". " + str(spisok[i])))
    #await message.reply('Введите частоту вывода уведомлений (Месяц, Неделя, День, Час)')
    await message.reply('Введите номер сайта для которого хотите настроить уведомления')

async def cancel_handler(message: types.Message, state: FSMContext):
        if message.text.strip() == "отмена" or "Отмена":
            current_state = await state.get_state()
            if current_state is None:
                await message.answer('Вам нечего отменять =)')
                await message.delete()
                return
            await state.finish()
            await message.reply('Вы вернулись в главное меню')

async def set_site(message: types.Message, state:FSMContext):
    if message.text.isdigit():
        if int(message.text) == 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9 or 10:
            check = int(message.text.strip())
            for_amount = list()
            for_amount = sqlite_db.sql_read_user(message.from_user.id)
            amount = len(for_amount)
            if check <= amount:
                async with state.proxy() as data:
                    data['number'] = message.text
                await message.reply("Вы выбрали: " + str(message.text))
                site_info.number = int(message.text)
                site_info.uid = sqlite_db.sql_get_uid(str(message.from_user.id))
                site_info.uid = str(site_info.uid[int(message.text)-1])
                site_info.uid = re.sub(r'[,\'\"\(\)]', '', site_info.uid)
                site_info.date = sqlite_db.sql_get_last_date(site_info.uid)
                spisok = sqlite_db.sql_get_url(str(message.from_user.id))
                #uid = sqlite_db.sql_get_uid(str(message.from_user.id))
                i = int(message.text)
                url = str(spisok[i-1]) 
                url1 = str(spisok[i-1])
                url = re.sub(r'[,\'\"\(\)]', '', url)
                url1 = re.sub(r'[,\'\"\(\)]', '', url1)
                url1 = str("http://" + url1)
                print(url)
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
                    site_info.site_url = url
                    site_info.status = "Offline"
                    site_info.ping = "None"
                    site_info.check_date = datetime.now()
                    await sqlite_db.sql_update_site(site_info.uid, site_info.status, site_info.ping, site_info.check_date)
                    await sqlite_db.sql_add_sitelog(site_info.uid, url, site_info.status, site_info.ping, site_info.check_date)
                else:
                    await message.reply("Сайт работает!")
                    ping_only = ping(url , size=1, count=1)
                    ping_only = str(ping_only.rtt_avg_ms) + " ms"
                    site_info.ping = ping_only
                    await message.answer("Время отклика: " + ping_only)
                    site_info.site_url = url
                    site_info.status = "Online"
                    site_info.check_date = datetime.now()
                    await sqlite_db.sql_update_site(site_info.uid, site_info.status, site_info.ping, site_info.check_date)
                    await sqlite_db.sql_add_sitelog(site_info.uid, url, site_info.status, site_info.ping, site_info.check_date)
                #print(site_info.uid)
                #print(site_info.date)
                await message.reply('Введите частоту вывода уведомлений (Месяц, Неделя, День, Час)')
                await FSMNotify.next()
            else:
                await message.answer("Введенный номер превышает количество сайтов в списке")
        else:
            await message.answer('Неправильно введен номер, повторите попытку')
    else:
        await message.answer ('Неправильно введен номер, повторите попытку')


async def set_freq(message: types.Message, state: FSMContext):
    if (message.text == "Месяц"):
        async with state.proxy() as data:
            data['freq'] = message.text
        await message.answer('Вы установили частоту вывода уведомлений: Месяц')
        #schedule.every()
        await FSMNotify.next()
    elif(message.text == "Неделя"):
        async with state.proxy() as data:
            data['freq'] = message.text
        await message.answer('Вы установили частоту вывода уведомлений: Неделя')
        #schedule.every(1).minute.do(await sqlite_db.sql_update_site(site_info.uid))
        
        

        thread = Thread(target=run())
        thread.start()
        
        await FSMNotify.next()
    elif(message.text == "День"):
        async with state.proxy() as data:
            data['freq'] = message.text
        await message.answer('Вы установили частоту вывода уведомлений: День')
        
        await FSMNotify.next()
    elif(message.text == "Час"):
        async with state.proxy() as data:
            data['freq'] = message.text
        await message.answer('Вы установили частоту вывода уведомлений: Час')
        
        await FSMNotify.next()
    else:
        await message.reply("Вы ввели неверную частоту (Пример: Месяц/Неделя/День/Час)")  




def register_handlers_Notify(dp:Dispatcher):
    dp.register_message_handler(cm_start, commands=['Уведомление'], state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена' or 'Отмена', ignore_case=True), state="*")
    dp.register_message_handler(set_site, state=FSMNotify.number)
    dp.register_message_handler(set_freq, state=FSMNotify.freq)
   
