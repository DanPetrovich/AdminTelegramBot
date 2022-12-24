from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
import logging
import config
import inline_keyboard

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)

users = {}


class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()
    adminlist = State()
    pin_message = State()
    unpin_message = State()


async def admin_check(message: types.Message):
    for admin in (await bot.get_chat_administrators(chat_id=message.chat.id)):
        if admin["user"]["id"] == message.from_user.id:
            return True
    return False


async def update(message: types.Message):
    for member in message.new_chat_members:
        users['@' + member.username] = member.id
        print(users)


@dp.message_handler(commands=['start'])
async def show_admin_buttons(message: types.Message):
    if await admin_check(message):
        await message.answer(text='всем привет!', reply_markup=inline_keyboard.markup)
        await dialog.adminlist.set()
    else:
        await message.answer(text='У тебя тут нет власти')


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def message_for_new_member(message: types.Message):
    await message.answer(text='Привет, новичок')
    await update(message)


@dp.message_handler(content_types='text', text='Добавить Админа')
async def add_admin(message: types.Message):
    print("Добавить Админа")
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Введите никнейм или id юзера, которого хотите сделать админом'
        await message.answer(text=output, reply_markup=keyboard)
        await dialog.adminlist.set()
    else:
        output = 'ручонки шаловливые свои на стол! тебе нельзя'
        await message.answer(text=output)


@dp.message_handler(state=dialog.adminlist)
async def make_admin(message: types.Message, state: FSMContext):
    print("add admin")
    try:
        user_id = int(users[message.text.strip(' ')])
        await bot.promote_chat_member(chat_id=message.chat.id, user_id=user_id, can_manage_chat=True,
                                      can_change_info=True,
                                      can_delete_messages=True,
                                      can_manage_video_chats=True,
                                      can_promote_members=True,
                                      can_pin_messages=True,
                                      can_edit_messages=True,
                                      can_post_messages=True,
                                      can_restrict_members=True,
                                      can_invite_users=True)
        await message.answer('поздравляю, еще один админ')
    except KeyError:
        await message.reply('такого не знаю')
    await state.finish()


@dp.message_handler(content_types='text', text='Забанить кого-то')
async def ban_user(message: types.Message):
    print("Забанить кого-то")
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Введите никнейм или id юзера, которого хотите забанить'
        await message.answer(text=output, reply_markup=keyboard)
        await dialog.blacklist.set()
    else:
        output = 'ручонки шаловливые свои на стол! тебе нельзя'
        await message.answer(text=output)


@dp.message_handler(state=dialog.blacklist)
async def blacklist(message: types.Message, state: FSMContext):
    print("ban")
    try:
        user_id = int(users[message.text.strip(' ')])
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.answer('бан прошел успешно')
    except KeyError:
        await message.reply('такого не знаю')

    await state.finish()


@dp.message_handler(content_types='text', text='Разбанить кого-то')
async def unban_user(message: types.Message):
    print("Разбанить кого-то")
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Введите никнейм или id юзера, которого хотите разбанить'
        await message.answer(text=output, reply_markup=keyboard)
        await dialog.whitelist.set()
    else:
        output = 'ручонки шаловливые свои на стол! тебе нельзя'
        await message.answer(text=output)


@dp.message_handler(state=dialog.whitelist)
async def whitelist(message: types.Message, state: FSMContext):
    print("unban")
    try:
        user_id = int(users[message.text.strip(' ')])
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.answer('разбан прошел успешно')
    except KeyError:
        await message.reply('такого не знаю')
    await state.finish()


@dp.message_handler(content_types='text', text='Получить статистику')
async def get_statistic(message: types.Message):
    await message.answer(
        f"Количество обычных смертных: {len(await bot.get_chat_administrators(chat_id=message.chat.id)) - 1} \n"
        f"Количество богов: {await bot.get_chat_member_count(chat_id=message.chat.id)}")


@dp.message_handler(content_types='text', text='Заставить уйти')
async def leave(message: types.Message):
    await bot.leave_chat(chat_id=message.chat.id)


@dp.message_handler(content_types='text', text='Закрепить сообщение')
async def pin_mess(message: types.Message):
    if await admin_check(message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        output = 'Введите сообщение, которое надо закрепить'
        await message.answer(text=output, reply_markup=keyboard)
        await dialog.pin_message.set()


@dp.message_handler(state=dialog.pin_message)
async def pin_message(message: types.Message, state: FSMContext):
    try:
        await bot.pin_chat_message(message.chat.id, message.message_id)
        await message.reply('Успешно')
    except:
        await message.reply('упс, что-то пошло не по плану')
    await state.finish()


@dp.message_handler(content_types='text', text='Открепить сообщение')
async def unpin_mess(message: types.Message):
    if await admin_check(message):
        try:
            await bot.unpin_chat_message(message.chat.id)
            await message.reply('Успешно')
        except:
            await message.reply('упс, что-то пошло не по плану')


@dp.message_handler()
async def fun(message: types.Message):
    await update(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
