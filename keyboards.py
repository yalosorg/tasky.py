from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

kbtl1 = KeyboardButton('/День')
kbtl2 = KeyboardButton('/Месяц')
kbtl3 = KeyboardButton('/Год')

kb_task_length = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
kb_task_length.row(kbtl1, kbtl2, kbtl3)