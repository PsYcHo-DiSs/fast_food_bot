import os

from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.orm import mapped_column, Session
from sqlalchemy import String, Integer, BigInteger, DECIMAL, ForeignKey
from sqlalchemy import create_engine, UniqueConstraint
from dotenv import load_dotenv

load_dotenv()

BD_USER = os.getenv('DB_USER')
BD_PASSWORD = os.getenv('DB_PASSWORD')
BD_ADDRESS = os.getenv('DB_ADDRESS')
BD_PORT = os.getenv('DB_PORT')
BD_NAME = os.getenv('DB_NAME')

MEDIA_DIRECTORY = os.getenv('MEDIA_FOLDER')

engine = create_engine(f'postgresql://{BD_USER}:{BD_PASSWORD}@{BD_ADDRESS}:{BD_PORT}/{BD_NAME}', echo=False)


class Base(DeclarativeBase):
    pass


class Users(Base):
    """База пользователей"""
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    carts: Mapped[int] = relationship('Carts', back_populates='user_cart')

    def __str__(self):
        return self.name


class Carts(Base):
    """Временная корзина покупателя, используется до кассы"""
    __tablename__ = 'carts'
    id: Mapped[int] = mapped_column(primary_key=True)
    total_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)

    user_cart: Mapped[Users] = relationship(back_populates='carts')
    final_id: Mapped[int] = relationship('FinalCarts', back_populates='user_cart')

    def __str__(self):
        return str(self.id)


class FinalCarts(Base):
    """Окончательная корзина пользователя, возле кассы"""
    __tablename__ = 'final_carts'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(50))
    final_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), default=0)
    quantity: Mapped[int]

    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.id'))
    user_cart: Mapped[Carts] = relationship(back_populates='final_id')

    __table_args__ = (UniqueConstraint('cart_id', 'product_name'),)

    def __str__(self):
        return str(self.id)


class Categories(Base):
    """Категории продуктов"""
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(20), unique=True)

    products: Mapped['Products'] = relationship(back_populates='product_category')

    def __str__(self):
        return self.category_name


class Products(Base):
    """Продукты"""
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String(100))
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    product_category: Mapped[Categories] = relationship(back_populates='products')


def main():
    Base.metadata.create_all(engine)
    categories = ('Лаваши', 'Донары', 'Хот-Доги', 'Десерты', 'Соусы', 'Напитки')
    products = (
        (1, 'Мини Лаваш', 20000, 'Мясо, тесто, помидоры', f'{MEDIA_DIRECTORY}/lavash/lavash_1.jpg'),
        (1, 'Мини Говяжий', 22000, 'Мясо, тесто, помидоры', f'{MEDIA_DIRECTORY}/lavash/lavash_2.jpg'),
        (1, 'Мини с сыром', 24000, 'Мясо, тесто, помидоры', f'{MEDIA_DIRECTORY}/lavash/lavash_3.jpg'),
        (2, 'Донар со свининой', 18000, 'Свинина, тесто, овощи', f'{MEDIA_DIRECTORY}/donar/donar_1.jpg'),
        (2, 'Донар с курицей', 22000, 'Курица, тесто, овощи', f'{MEDIA_DIRECTORY}/donar/donar_2.jpg'),
        (2, 'Донар с говядиной', 19000, 'Говядина, тесто, овощи', f'{MEDIA_DIRECTORY}/donar/donar_3.jpg'),
    )

    with Session(engine) as session:
        for category in categories:
            query = Categories(category_name=category)
            session.add(query)
        session.commit()

        for product in products:
            query = Products(
                category_id=product[0],
                product_name=product[1],
                price=product[2],
                description=product[3],
                image=product[4]
            )

            session.add(query)
        session.commit()


if __name__ == '__main__':
    main()
