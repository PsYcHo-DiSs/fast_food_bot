import asyncio
import os
from os import getenv

from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
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
        await show_main_menu(message)
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

    await show_main_menu(message)


async def show_main_menu(message: Message):
    """Сделать заказ, История, Корзинка, Настройки"""
    await message.answer(text='Выберите направление',
                         reply_markup=generate_main_menu())


@dp.message(F.text == '✔️ Сделать заказ')
async def make_order(message: Message):
    """Реакция на кнопку Сделать заказ"""
    chat_id = message.chat.id
    # TODO Получить id корзины пользователя

    await bot.send_message(chat_id=chat_id,
                           text='Погнали нахуй!',
                           reply_markup=back_to_main_menu())
    await message.answer(text='Выберите категорию',
                         reply_markup=generate_category_menu())


@dp.message(F.text.regexp(r'^Г[а-я]+ [а-я]{4}'))  # @dp.message(F.text == 'Главное меню')
async def return_to_main_menu(message: Message):
    """Реакция на кнопку Главное меню"""
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await show_main_menu(message)


@dp.callback_query(F.data.regexp(r'category_[1-9]'))
async def show_product_button(callback: CallbackQuery):
    """Показ всех продуктов выбранной категории"""
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    category_id = int(callback.data.split('_')[1])
    await bot.edit_message_text(text='Выберите продукт',
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=show_product_by_category(category_id))


@dp.callback_query(F.data == 'return_to_category')
async def return_to_category_button(callback: CallbackQuery):
    """Возврат к выбору категории продукта"""
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='Выберите категорию',
                                reply_markup=generate_category_menu())


@dp.callback_query(F.data.contains('product_'))
async def show_product_detail(callback: CallbackQuery):
    """Показ выбранного продукта"""
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    product_id = int(callback.data.split('_')[1])
    product = db_get_product_by_id(product_id)
    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)
    if user_cart_id := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart_id)

        text = f'<b>{product.product_name}</b>\n\n'
        text += f'<b>Ингредиенты:</b> {product.description}\n'
        text += f'<b>Цена:</b> {product.price} сум'

        await bot.send_photo(chat_id=chat_id,
                             photo=FSInputFile(path=product.image),
                             caption=text)
    else:
        await bot.send_message(chat_id=chat_id,
                               text='К сожалению, у нас нет вашего контакта!',
                               reply_markup=share_phone_button())


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
