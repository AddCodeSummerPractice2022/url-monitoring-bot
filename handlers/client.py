from aiogram import Dispatcher, types
from createBot import dp, bot
from keyboards import kb_client

#@dp.message_handler(commands=['start', 'help'])
async def command_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, 'flex', reply_markup=kb_client)
        #await message.delete()
    except:
        await message.reply('Начните общение с ботом через ЛС: \nhttps://t.me/avaicheck_bot')

#@dp.message_handler(commands=['end'])
async def command_end(message : types.Message):
    await bot.send_message(message.from_user.id, 'Пока', reply_markup=kb_client)

# @dp.message_handler(commands='add')

def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_end, commands=['end'])