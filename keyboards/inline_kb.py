from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_utills import db_get_all_category, db_get_products, db_get_total_final_price


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    """Кнопки категорий"""
    categories = db_get_all_category()
    total_final_price = db_get_total_final_price(chat_id) or 0
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Ваша корзинка ({total_final_price} сум)', callback_data='Ваша корзинка')
    [builder.button(text=category.category_name,
                    callback_data=f'category_{category.id}') for category in categories]

    builder.adjust(1, 2)

    return builder.as_markup()


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    """Кнопки продуктов"""
    products = db_get_products(category_id)
    builder = InlineKeyboardBuilder()
    [builder.button(text=product.product_name,
                    callback_data=f'product_{product.id}') for product in products]
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text='🔙 Назад',
                             callback_data='return_to_category')
    )

    return builder.as_markup()


def generate_constructor_button(quantity=1) -> InlineKeyboardMarkup:
    """Кнопки выбора количества продуктов + -"""
    builder = InlineKeyboardBuilder()
    builder.button(text='➖', callback_data='action -')
    builder.button(text=f'{quantity}', callback_data=f'noop_{quantity}')
    builder.button(text='➕', callback_data='action +')
    builder.button(text='Положить в корзину 🛒', callback_data='put_into_Cart')

    builder.adjust(3, 1)
    return builder.as_markup()
