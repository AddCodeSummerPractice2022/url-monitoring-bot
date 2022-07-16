from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/Добавить')
b2 = KeyboardButton('/Список')
b3 = KeyboardButton('/Удалить')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_client.add(b1).insert(b3).add(b2)