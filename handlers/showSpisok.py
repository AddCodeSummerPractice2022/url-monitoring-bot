from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram import types, Dispatcher
from createBot import dp
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db

class get_spisok_bd():
    tg_user_id = str()
    site_url = list(str())
    status = str()
    ping = str()
    check_date = str()
    


async def show_spisok(message: types.Message):
    get_spisok_bd.tg_user_id = str(message.from_user.id)
    spisok = sqlite_db.sql_get_spisok(str(message.from_user.id))
    await message.answer("Вывожу Ваш список сайтов на мониторинг")
    for i in range(len(spisok)):
        await message.answer(str("   " + str(i+1) + ". " + str(spisok[i])))
    
def register_handlers_showSpisok(dp : Dispatcher):
    dp.register_message_handler(show_spisok, commands=['Список'])

