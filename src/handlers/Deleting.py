from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from data_base import sqlite_db


class FSMDelete(StatesGroup):
    number = State()
    answer = State()


class number():
    number = int()


async def delete_start(message: types.Message):
    await FSMDelete.number.set()
    # await message.reply("Вывожу ваш список сайтов на мониторинг")
    For_Spisok = sqlite_db.sql_get_spisok(str(message.from_user.id))
    await message.answer("Вывожу Ваш список сайтов на мониторинг")
    for i in range(len(For_Spisok)):
        await message.answer(str("   " + str(i + 1) + ". " + str(For_Spisok[i])))
    await message.answer("Введите номер сайта из списка, который хотите удалить")


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


async def load_number(message: types.Message, state: FSMContext):
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
                number.number = int(message.text)
                await message.answer("Вы уверены, что хотите удалить данный сайт из списка мониторинга? (ДА/НЕТ)")
                await FSMDelete.next()
            else:
                await message.answer("Введенный номер превышает количество сайтов в списке")
        else:
            await message.answer('Неправильно введен номер, повторите попытку')
    else:
        await message.answer('Неправильно введен номер, повторите попытку')


async def load_answer(message: types.Message, state: FSMContext):
    if message.text.strip() == "ДА":
        async with state.proxy() as data:
            data['answer'] = message.text
        await message.answer("Удаление завершено!")
        sqlite_db.sql_remove_site(message.from_user.id, number.number)
        await state.finish()
    elif message.text.strip() == "НЕТ":
        async with state.proxy() as data:
            data['number'] = message.text
        await message.reply("Хорошо, отменяю удаление")
        await state.finish()
    else:
        await message.reply("Неправильный ответ, повторите попытку")


def register_handlers_Deleting(dp: Dispatcher):
    dp.register_message_handler(delete_start, commands=['Удалить'], state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена' or 'Отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_number, state=FSMDelete.number)
    dp.register_message_handler(load_answer, state=FSMDelete.answer)
