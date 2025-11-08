import logging
from typing import Sequence
from uuid import UUID

import allure
from allure_commons.types import AttachmentType
from sqlalchemy import create_engine, Engine, event
from sqlmodel import Session, select

from models.spend import Category
from models.spend import Spend


class SpendDb:
    engine: Engine

    def __init__(self, db_url: str):
        self.engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 3,
                "gssencmode": "disable",
            },
        )
        event.listen(self.engine, "before_cursor_execute", fn=self.attach_sql)
        logging.info(f"Подключение к БД трат: {db_url}")

    @staticmethod
    def attach_sql(conn, cursor, statement, parameters, context, executemany):
        try:
            statement_with_params = statement % parameters if parameters else statement
            name = f"SQL {statement.split(' ')[0]} - {context.engine.url.database}"
            allure.attach(statement_with_params, name=name, attachment_type=AttachmentType.TEXT)
        except Exception:
            allure.attach(statement, name=f"SQL - {context.engine.url.database}", attachment_type=AttachmentType.TEXT)

    @allure.step("[БД] Получить категории пользователя: {username}")
    def get_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            categories = session.exec(statement).all()
            logging.info(f"Получено категорий для пользователя {username}: {len(categories)}")
            return categories

    @allure.step("[БД] Получить категорию по ID: {category_id}")
    def get_category_by_id(self, category_id):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.id == category_id)
            category = session.exec(statement).first()
            logging.debug(f"Категория с ID {category_id}: {'найдена' if category else 'не найдена'}")
            return category

    @allure.step("[БД] Получить категорию по имени: {category_name}")
    def get_category_by_name(self, category_name):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.name == category_name)
            category = session.exec(statement).first()
            logging.debug(f"Категория '{category_name}': {'найдена' if category else 'не найдена'}")
            return category

    @allure.step("[БД] Удалить категорию: {category_id}")
    def delete_category(self, category_id: UUID):
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            if category:
                session.delete(category)
                session.commit()
                logging.info(f"Категория удалена: {category_id}")
            else:
                logging.warning(f"Категория не найдена для удаления: {category_id}")

    @allure.step("[БД] Удалить категорию по имени: {category_name}")
    def delete_category_by_name(self, category_name: str):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.name == category_name)
            category = session.exec(statement).first()
            if category:
                session.delete(category)
                session.commit()
                logging.info(f"Категория удалена: {category_name}")
            else:
                logging.warning(f"Категория '{category_name}' не найдена для удаления")

    @allure.step("[БД] Получить трату по ID: {spend_id}")
    def get_spend_by_id(self, spend_id):
        with Session(self.engine) as session:
            statement = select(Spend).where(Spend.id == spend_id)
            spend = session.exec(statement).first()
            logging.debug(f"Трата с ID {spend_id}: {'найдена' if spend else 'не найдена'}")
            return spend

    @allure.step("[БД] Удалить трату: {spend_id}")
    def delete_spend(self, spend_id: str):
        with Session(self.engine) as session:
            spend = session.get(Spend, spend_id)
            if spend:
                session.delete(spend)
                session.commit()
                logging.info(f"Трата удалена: {spend_id}")
            else:
                logging.warning(f"Трата не найдена для удаления: {spend_id}")
