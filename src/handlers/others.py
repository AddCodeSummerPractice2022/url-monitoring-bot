from aiogram import Dispatcher, types
from createBot import dp

# Обработка неизвестных команд
async def empty(message : types.Message):
        await message.answer('Нет такой команды')
        await message.delete()

def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(empty)