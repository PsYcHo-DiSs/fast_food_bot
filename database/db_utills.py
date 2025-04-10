from typing import Iterable

from sqlalchemy import update, select, delete, DECIMAL, ScalarResult
from sqlalchemy.sql.functions import sum
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

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
    """Получаем все продукты выбранной категории с id категории"""
    query = select(Products).where(Products.category_id == category_id)
    return db_session.scalars(query)


def db_get_product_by_id(product_id: int) -> Products:
    """Получаем продукт по его ID"""
    query = select(Products).where(Products.id == product_id)
    return db_session.scalar(query)


def db_get_user_cart(chat_id: int) -> Carts:
    """Получаем корзинку пользователя по связанной таблице Users"""
    query = select(Carts).join(Users).where(Users.telegram == chat_id)
    return db_session.scalar(query)


def db_update_to_cart(price: DECIMAL, cart_id: int, quantity=1) -> None:
    """Обновляем данные временной корзины"""
    query = update(Carts
                   ).where(Carts.id == cart_id
                           ).values(total_products=quantity,
                                    total_price=price)
    db_session.execute(query)
    db_session.commit()


def db_get_product_by_name(product_name: str) -> Products:
    """Получаем продукт по его названию"""
    query = select(Products).where(Products.product_name == product_name)
    return db_session.scalar(query)


def db_get_final_carts_by_chat_id(chat_id: int) -> ScalarResult[FinalCarts]:
    query = select(FinalCarts
                   ).join(Carts
                          ).join(Users
                                 ).where(Users.telegram == chat_id)

    return db_session.scalars(query)


def db_get_final_cart_entry(product_name: str, cart_id: int) -> FinalCarts:
    """Получить запись в финальной корзине пользователя по названию товара"""
    query = select(FinalCarts).where(FinalCarts.product_name == product_name,
                                     FinalCarts.cart_id == cart_id)
    return db_session.scalar(query)


def upsert_final_cart(product_name: str, total_price: DECIMAL, total_products: int, cart_id: int) -> None:
    """Добавляем товар в корзину, если его нет, иначе обновляем количество и цену"""
    existing_final_cart = db_get_final_cart_entry(product_name, cart_id)

    if existing_final_cart:
        query = update(FinalCarts).where(
            (FinalCarts.product_name == product_name) & (FinalCarts.cart_id == cart_id)
        ).values(
            final_price=existing_final_cart.final_price + total_price,
            quantity=existing_final_cart.quantity + total_products
        )

        db_session.execute(query)

    else:
        query = FinalCarts(product_name=product_name,
                           final_price=total_price,
                           quantity=total_products,
                           cart_id=cart_id)

        db_session.add(query)

    db_session.commit()


def db_get_total_final_price(chat_id: int) -> DECIMAL:
    """Получение общей суммы к оплате из постоянной корзины пользователя"""
    query = select(sum(FinalCarts.final_price)
                   ).join(Carts
                          ).join(Users
                                 ).where(Users.telegram == chat_id)
    return db_session.execute(query).fetchone()[0]


def db_get_final_products_for_edit(chat_id: int) -> Iterable:
    """Получаем данные из итоговой корзинки для редактирования"""
    try:
        query = select(FinalCarts).join(Carts).join(Users).where(Users.telegram == chat_id)
        result = db_session.execute(query).all()

        if not result:
            raise ValueError(f"Нет продуктов для пользователя с chat_id {chat_id}.")

        return [row[0] for row in result]

    except SQLAlchemyError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        raise ConnectionError("Ошибка подключения к базе данных.")

    except ValueError as e:
        print(f"Ошибка: {e}")
        raise e


def db_delete_product_by_final_cart_id(f_cart_id: int) -> None:
    """Удаление товара из финальной корзины по id записи товара"""
    query = delete(FinalCarts).where(FinalCarts.id == f_cart_id)
    db_session.execute(query)
    db_session.commit()


def db_get_product_by_final_cart_id(f_cart_id: int) -> FinalCarts:
    """Возвращает запись товара из финальной корзины по id финальной корзины"""
    try:
        query = select(FinalCarts).where(FinalCarts.id == f_cart_id)
        product = db_session.scalar(query)

        if product is None:
            raise ValueError(f"Продукт с ID {f_cart_id} не найден.")

        return product

    except SQLAlchemyError as e:
        # Логирование ошибки в базу данных или файл
        print(f"Ошибка при работе с базой данных: {e}")
        raise ConnectionError("Ошибка подключения к базе данных.")

    except ValueError as e:
        # Логирование ошибки в файл
        print(f"Ошибка: {e}")
        raise e  # Перебрасываем исключение, чтобы обработать его на уровне вызывающей функции


def db_update_final_cart_product(f_cart_id: int, final_price: DECIMAL, quantity: int) -> None:
    """Обновляет запись о продукте в финальной корзинке пользователя"""
    try:
        query = update(FinalCarts).where(FinalCarts.id == f_cart_id).values(final_price=final_price, quantity=quantity)
        result = db_session.execute(query)
        db_session.commit()

        if result.rowcount == 0:
            raise ValueError(f"Продукт с ID {f_cart_id} не найден для обновления.")

    except SQLAlchemyError as e:
        db_session.rollback()  # откат транзакции в случае ошибки
        print(f"Ошибка при обновлении в базе данных: {e}")
        raise ConnectionError("Ошибка при работе с базой данных.")

    except ValueError as e:
        print(f"Ошибка: {e}")
        raise e  # Перебрасываем исключение на более высокий уровень


def db_get_user_by_chat_id(chat_id: int) -> Users:
    """Получение пользователя по его телеграмм id"""
    query = select(Users).where(Users.telegram == chat_id)
    return db_session.scalar(query)


def db_clear_final_cart(cart_id: int) -> None:
    """Очистка финальной корзинки по телеграм id временной корзинки"""
    query = delete(FinalCarts).where(FinalCarts.cart_id == cart_id)
    db_session.execute(query)
    db_session.commit()
