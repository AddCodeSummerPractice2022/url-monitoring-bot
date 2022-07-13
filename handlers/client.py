from aiogram import Dispatcher, types
from createBot import dp, bot
from keyboards import kb_client

async def command_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Привет! Я бот, который проверяет состояние сайтов. Командой Добавить, Вы можете добавить сайт на мониторинг', reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply('Начните общение с ботом через ЛС: \nhttps://t.me/avaicheck_bot')

async def command_end(message : types.Message):
    await bot.send_message(message.from_user.id, 'Пока', reply_markup=kb_client)

def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_end, commands=['end'])