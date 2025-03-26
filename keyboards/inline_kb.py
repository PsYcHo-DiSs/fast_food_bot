from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utills import db_get_all_category


def generate_category_menu() -> InlineKeyboardMarkup:
    """Кнопки категорий"""
    categories = db_get_all_category()
    builder = InlineKeyboardBuilder()
    # TODO Общая сумма корзинки
    builder.button(text=f'Ваша корзинка (TODO сум)', callback_data='Ваша корзинка')
    [builder.button(text=category.category_name,
                    callback_data=f'category_{category.id}') for category in categories]

    builder.adjust(1, 2)

    return builder.as_markup()
