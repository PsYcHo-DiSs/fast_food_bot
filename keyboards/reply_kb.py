from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup


def share_phone_button() -> ReplyKeyboardMarkup:
    """Кнопка для отправки контакта"""
    builder = ReplyKeyboardBuilder()
    builder.button(text='Отправить свой контакт ☎️', request_contact=True)

    return builder.as_markup(resize_keyboard=True)


def generate_main_menu() -> ReplyKeyboardMarkup:
    """Кнопки основного меню"""
    builder = ReplyKeyboardBuilder()
    builder.button(text='✔️ Сделать заказ')
    builder.button(text='📖 История')
    builder.button(text='🛒 Корзинка')
    builder.button(text='⚙️ Настройки')
    builder.adjust(1, 3)

    return builder.as_markup(resize_keyboard=True)


def back_to_main_menu() -> ReplyKeyboardMarkup:
    """Кнопка главного меню"""
    builder = ReplyKeyboardBuilder()
    builder.button(text='Главное меню')

    return builder.as_markup(resize_keyboard=True)


def back_arrow_button() -> ReplyKeyboardMarkup:
    """Кнопка назад из подробностей о продукте"""
    builder = ReplyKeyboardBuilder()
    builder.button(text='↩ Назад')
    return builder.as_markup(resize_keyboard=True)
