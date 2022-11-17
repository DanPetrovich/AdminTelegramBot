from aiogram import types

markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

menu = [types.KeyboardButton('Добавить Админа'),
        types.KeyboardButton('Забанить кого-то'), types.KeyboardButton('Разбанить кого-то'),
        types.KeyboardButton('Получить статистику'),
        types.KeyboardButton('Заставить уйти'),
        types.KeyboardButton('Закрепить сообщение'),
        types.KeyboardButton('Открепить сообщение')]

for item in menu:
    markup.add(item)
