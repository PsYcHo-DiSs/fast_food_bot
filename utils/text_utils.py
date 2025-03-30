def text_for_caption(name, description, price) -> str:
    """Формирование текстовой подписи для товара"""

    text = (f"<b>{name}</b>\n\n"
            f"<b>Ингредиенты:</b> {description}\n"
            f"<b>Цена:</b> {price} сум")

    return text
