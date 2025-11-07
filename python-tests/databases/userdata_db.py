import logging
from typing import Sequence, Optional

import allure
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import ScalarResult
from sqlmodel import Session, select

from models.user import User
from utils.allure_helpers import attach_sql


class UserdataDB:

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
        event.listen(self.engine, 'before_cursor_execute', fn=attach_sql)
        logging.info(f"Подключение к БД пользователей: {db_url}")

    @allure.step('[БД] Получить данные пользователя: {username}')
    def get_userdata_by_username(self, username: str) -> Optional[User]:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            result: ScalarResult[User] = session.exec(statement)
            user = result.one_or_none()
            logging.debug(f"Пользователь '{username}': {'найден' if user else 'не найден'}")
            return user

    @allure.step('[БД] Получить все записи пользователя: {username}')
    def get_all_records_by_username(self, username: str) -> Sequence[User]:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            result: ScalarResult[User] = session.exec(statement)
            users = result.all()
            logging.info(f"Найдено записей для пользователя '{username}': {len(users)}")
            return users
