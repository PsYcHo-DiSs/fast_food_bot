from sqlalchemy import DECIMAL, ScalarResult

from database.models import FinalCarts
from database.db_utills import db_get_final_carts_by_chat_id


def text_for_caption(name: str, description: str, price: DECIMAL) -> str:
    """Формирование текстовой подписи для товара"""

    text = (f"<b>{name}</b>\n\n"
            f"<b>Ингредиенты:</b> {description}\n"
            f"<b>Цена:</b> {price} сум")

    return text


def counting_products_from_final_carts(chat_id: int, user_text: str) -> tuple:
    """Формирование истории заказа (содержимого итоговой корзины)"""

    final_carts = db_get_final_carts_by_chat_id(chat_id)

    text = f"<b>{user_text}:</b>\n\n"
    total_final_qty = total_final_price = count = 0
    cart_id = None

    for count, cart in enumerate(final_carts, 1):
        if cart_id is None:
            cart_id = cart.cart_id
        total_final_qty += cart.quantity
        total_final_price += cart.final_price
        text += (f"<b>{count}.</b> {cart.product_name}\n"
                 f"<b>Количество:</b> {cart.quantity} шт.\n"
                 f"<b>Стоимость:</b> {cart.final_price}\n\n")

    if count == 0:
        return 0, 'Ваша корзина пока пуста 😞, желаете сделать заказ? 💰', 0, 0

    text += (f"<b>Общее количество продуктов:</b> {total_final_qty} шт.\n"
             f"<b>Общая стоимость корзины:</b> {total_final_price} сум")

    return count, text, total_final_price, cart_id
