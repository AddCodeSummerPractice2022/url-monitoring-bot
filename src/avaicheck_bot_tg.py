from aiogram.utils import executor
from createBot import dp
from data_base import sqlite_db


async def on_startup(_):
    print('Бот вошел в чатик')
    sqlite_db.sql_start_tables()

from handlers import addSite, client, others, showSpisok, Deleting

client.register_handlers_client(dp)
addSite.register_handlers_addSite(dp)
showSpisok.register_handlers_showSpisok(dp)
Deleting.register_handlers_Deleting(dp)
others.register_handlers_other(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)