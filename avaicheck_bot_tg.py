
from aiogram.utils import executor
from createBot import dp



async def on_startup():
    print('Бот вошел в чатик')

from handlers import client, admin, others

client.register_handlers_client(dp)
others.register_handlers_other(dp)


executor.start_polling(dp, skip_updates=True)
