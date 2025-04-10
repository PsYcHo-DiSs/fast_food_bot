import asyncio
import os
from os import getenv

from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, LabeledPrice
from aiogram.exceptions import TelegramBadRequest
from dotenv import load_dotenv

from keyboards.inline_kb import *
from keyboards.reply_kb import *
from database.db_utills import *
from utils.text_utils import *

load_dotenv()
TLG_TOKEN = getenv('TOKEN')
PAYMENT_TOKEN = getenv('CLICK_PAYMENT_TOKEN')
MANAGER_GROUP = getenv('MANAGER_GROUP_ORDERS')
MEDIA_FOLDER = getenv('MEDIA_FOLDER')
dp = Dispatcher()
bot = Bot(TLG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


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

    await bot.send_message(chat_id=chat_id,
                           text='Погнали нахуй!',
                           reply_markup=back_to_main_menu())
    await message.answer(text='Выберите категорию',
                         reply_markup=generate_category_menu(chat_id))


@dp.message(F.text.regexp(r'^Г[а-я]+ [а-я]{4}'))  # @dp.message(F.text == 'Главное меню')
async def return_to_main_menu(message: Message):
    """Реакция на кнопку Главное меню"""
    try:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id - 1)
    except TelegramBadRequest:
        ...
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
                                reply_markup=generate_category_menu(chat_id))


@dp.callback_query(F.data.contains('product_'))
async def show_product_detail(callback: CallbackQuery):
    """Показ выбранного продукта"""
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    product_id = int(callback.data.split('_')[1])
    product = db_get_product_by_id(product_id)
    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)
    if user_cart := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart.id)

        text = text_for_caption(name=product.product_name,
                                description=product.description,
                                price=product.price)

        await bot.send_message(chat_id=chat_id,
                               text='Выберите модификатор',
                               reply_markup=back_arrow_button())

        await bot.send_photo(chat_id=chat_id,
                             photo=FSInputFile(path=product.image),
                             caption=text,
                             reply_markup=generate_constructor_button())
    else:
        await bot.send_message(chat_id=chat_id,
                               text='К сожалению, у нас нет вашего контакта!',
                               reply_markup=share_phone_button())


@dp.message(F.text == '↩ Назад')
async def return_to_category_menu(message: Message):
    """Назад к выбору продукта по категории"""
    chat_id = message.chat.id
    message_id = message.message_id
    try:
        await bot.delete_message(chat_id=chat_id,
                                 message_id=message_id - 1)
    except TelegramBadRequest:
        ...
    await make_order(message)


@dp.callback_query(F.data.regexp(r'action [+-]'))
async def constructor_changer(callback: CallbackQuery):
    """Логика конструктора + -"""
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    product_name = callback.message.caption.split('\n')[0]
    product = db_get_product_by_name(product_name)
    user_cart = db_get_user_cart(chat_id)

    action = callback.data.split()[1]
    qty = user_cart.total_products
    price = product.price
    match action:
        case '+':
            qty += 1
        case '-':
            if qty < 2:
                await callback.answer('Меньше одного нельзя', show_alert=True)
            else:
                qty -= 1

    price *= qty
    db_update_to_cart(price=price,
                      cart_id=user_cart.id,
                      quantity=qty)

    text = text_for_caption(name=product.product_name,
                            description=product.description,
                            price=price)

    try:
        await bot.edit_message_caption(chat_id=chat_id,
                                       message_id=message_id,
                                       caption=text,
                                       reply_markup=generate_constructor_button(qty))
    except TelegramBadRequest:
        pass


@dp.callback_query(F.data == 'put_into_Cart')
async def put_into_final_carts(callback: CallbackQuery) -> None:
    """Добавление товара в корзину"""
    chat_id = callback.from_user.id
    message_id = callback.message.message_id
    product_name = callback.message.caption.split('\n')[0]
    user_cart = db_get_user_cart(chat_id)

    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    upsert_final_cart(product_name=product_name,
                      total_price=user_cart.total_price,
                      total_products=user_cart.total_products,
                      cart_id=user_cart.id)

    await bot.send_message(chat_id=chat_id, text='Товар(-ы) успешно добавлен(-ы) в вашу корзину ✅')
    await return_to_category_menu(callback.message)


@dp.callback_query(F.data == 'your_final_cart')
async def show_total_goods_list(callback: CallbackQuery, editor=False):
    """Показ содержимого финальной корзины"""
    chat_id = callback.from_user.id
    message_id = callback.message.message_id

    context = counting_products_from_final_carts(chat_id, 'Ваша корзина')
    # context returns (count, text, total_final_price, cart_id)
    count, text, *_ = context

    if editor:
        # вошли в режим редактирования финальной корзины
        if count:
            # если корзина НЕ пуста
            await bot.edit_message_caption(chat_id=chat_id,
                                           message_id=message_id,
                                           caption=text,
                                           reply_markup=generate_pay_edit_product(chat_id))

        else:
            # Пустая корзина
            await bot.send_message(chat_id=chat_id,
                                   text=text)

            await make_order(callback.message)

    else:
        # дефолтный режим, как есть
        await bot.delete_message(chat_id=chat_id, message_id=message_id)

        if count:
            # если корзина НЕ пуста
            await bot.send_photo(chat_id=chat_id,
                                 photo=FSInputFile(path=f"{MEDIA_FOLDER}/final_cart_img.jpg"),
                                 caption=text,
                                 reply_markup=generate_pay_edit_product(chat_id))
        else:
            # Пустая корзина
            await bot.send_message(chat_id=chat_id,
                                   text=text)

            await make_order(callback.message)


@dp.callback_query(F.data.regexp(r'delete_\d+'))
async def delete_final_cart_product(callback: CallbackQuery):
    """Реакция на кнопку с иксом для удаления"""
    f_cart_id = int(callback.data.split('_')[1])
    db_delete_product_by_final_cart_id(f_cart_id)
    await bot.answer_callback_query(callback_query_id=callback.id,
                                    text='Продукт удалён!')

    await show_total_goods_list(callback)


@dp.callback_query(F.data.regexp(r'^edit_\d+_[+-]$'))
async def final_cart_editor(callback: CallbackQuery):
    """Логика редактора продукта из финальной корзины"""
    chat_id = callback.from_user.id
    message_id = callback.message.message_id

    f_cart_id = int(callback.data.split('_')[1])
    action = callback.data.split('_')[2]

    product = db_get_product_by_final_cart_id(f_cart_id)
    # текущее состояние цены и количества
    cur_total_qty = product.quantity
    cur_total_price = product.final_price
    price_per_one = cur_total_price / cur_total_qty

    match action:
        case '-':
            product.quantity -= 1
            product.final_price -= price_per_one
        case '+':
            product.quantity += 1
            product.final_price += price_per_one

    if product.quantity:
        db_update_final_cart_product(f_cart_id=f_cart_id,
                                     final_price=product.final_price,
                                     quantity=product.quantity)
        await show_total_goods_list(callback, editor=True)
    else:
        db_delete_product_by_final_cart_id(f_cart_id)

        await bot.answer_callback_query(callback_query_id=callback.id,
                                        text=f'Продукт {product.product_name} удалён!')

        await show_total_goods_list(callback)


@dp.callback_query(F.data == 'order_pay')
async def create_order(callback: CallbackQuery):
    """Оплата продуктов"""
    chat_id = callback.from_user.id
    message_id = callback.message.message_id

    await bot.delete_message(chat_id=chat_id,
                             message_id=message_id)

    count, text, total_final_price, cart_id = (
        counting_products_from_final_carts(chat_id, 'Итоговый список для оплаты'))
    text += '\nДоставка по городу 10000 сум'

    text = text.replace('<b>', '').replace('</b>', '')

    await bot.send_invoice(chat_id=chat_id,
                           title='Ваш заказ',
                           description=text,
                           payload='bot-defined invoice payload',
                           provider_token=PAYMENT_TOKEN,
                           currency='UZS',
                           prices=[
                               LabeledPrice(label='Общая стоимость', amount=total_final_price * 100),
                               LabeledPrice(label='Доставка', amount=10000 * 100)
                           ])
    await bot.send_message(chat_id=chat_id,
                           text='Заказ оплачен!')

    await sending_report_to_manager(chat_id, text)
    # очистка финальной корзины пользователя после отправки информации менеджерам
    db_clear_final_cart(cart_id)


async def sending_report_to_manager(chat_id: int, text: str):
    """Отправка сообщения в чат группу"""
    user = db_get_user_by_chat_id(chat_id)
    text += f'\n\n<b>Имя заказчика: {user.name}\nКонтактный номер: {user.phone}</b>\n\n'
    await bot.send_message(chat_id=MANAGER_GROUP,
                           text=text)


@dp.message(F.text == r'🛒 Корзинка')
async def cart_from_main_menu(message: Message):
    await message.answer("Режим Разработки, учебный бот")


@dp.message(F.text == r'📖 История')
async def history_from_main_menu(message: Message):
    await message.answer("Режим Разработки,  учебный бот")


@dp.message(F.text == r'⚙️ Настройки')
async def setting_from_main_menu(message: Message):
    await message.answer("Режим Разработки, учебный бот ")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
