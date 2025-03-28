from typing import Iterable

from sqlalchemy.orm import Session
from sqlalchemy import update, delete, select, DECIMAL
from sqlalchemy.sql.functions import sum
from sqlalchemy.exc import IntegrityError

from .models import Users, Carts, FinalCarts, Categories, Products, engine

with Session(engine) as session:
    db_session = session


def db_registrate_user(full_name: str, chat_id: int) -> bool:
    """Первая регистрация пользователя с доступными данными"""
    try:
        query = Users(name=full_name, telegram=chat_id)
        db_session.add(query)
        db_session.commit()
        return False
    except IntegrityError:
        db_session.rollback()
        return True


def db_update_user(chat_id: int, phone: str) -> None:
    """Дополняем данные пользователя его телефоном"""
    query = update(Users).where(Users.telegram == chat_id).values(phone=phone)
    db_session.execute(query)
    db_session.commit()


def db_create_user_cart(chat_id: int) -> bool:
    """Создание временной корзины пользователя"""
    try:
        subquery = db_session.scalar(select(Users).where(Users.telegram == chat_id))
        query = Carts(user_id=subquery.id)
        db_session.add(query)
        db_session.commit()
        return True
    except IntegrityError:
        """Если карта уже существует"""
        db_session.rollback()
    except AttributeError:
        """Если контакт отправил анонимный пользователь"""
        db_session.rollback()


def db_get_all_category() -> Iterable:
    """Получаем все категории"""
    query = select(Categories)
    return db_session.scalars(query)


def db_get_products(category_id: int) -> Iterable:
    """Получаем все продукты выбранной категории о id категории"""
    query = select(Products).where(Products.category_id == category_id)
    return db_session.scalars(query)


def db_get_product_by_id(product_id: int) -> Products:
    """Получаем продукт по его ID"""
    query = select(Products).where(Products.id == product_id)
    return db_session.scalar(query)


def db_get_user_cart(chat_id: int) -> int:
    """Получаем ID корзинки по связанной таблице Users"""
    query = select(Carts.id).join(Users).where(Users.telegram == chat_id)
    return db_session.scalar(query)


def db_update_to_cart(price: DECIMAL, cart_id: int, quantity=1) -> None:
    """Обновляем данные временной корзины"""
    query = update(Carts
                   ).where(Carts.id == cart_id
                           ).values(total_products=quantity,
                                    total_price=price)
    db_session.execute(query)
    db_session.commit()
