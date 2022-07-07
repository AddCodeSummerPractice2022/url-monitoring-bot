from aiogram import Dispatcher, types
from createBot import dp

#@dp.message_handler()
async def echo_send(message : types.Message):
    #if message.text == 'привет' or 'Привет':
        await message.answer(message.text)
    #await message.reply(message.text)
    #await bot.send_message(message.from_user.id, message.text)


def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(echo_send)