import asyncio
import os
from os import getenv

from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from keyboards.inline_kb import *
from keyboards.reply_kb import *
from database.db_utills import *

load_dotenv()
TOKEN = getenv('TOKEN')
dp = Dispatcher()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def command_start(message: Message):
    """Старт бота"""
    await message.answer(f"Здравствуйте, <b>{message.from_user.full_name}!</b>, \n"
                         f"Вас приветствует бот доставки macros")
    await start_register_user(message)


async def start_register_user(message: Message):
    """Первая регистрация пользователя с проверкой на существование"""
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    if db_registrate_user(full_name, chat_id):
        await message.answer(text='Авторизация прошла успешно')
        # TODO Показать меню
    else:
        await message.answer(text='для связи с Вами нужен ваш контактный номер',
                             reply_markup=share_phone_button())


@dp.message(F.contact)
async def update_user_info_finish_register(message: Message):
    """Обновление данных пользователя его контактом"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    if db_create_user_cart(chat_id):
        await message.answer(text='Регистрация прошла успешно')

    # TODO Показать меню

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
