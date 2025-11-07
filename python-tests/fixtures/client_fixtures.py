import logging

import allure
import pytest
from faker import Faker

from clients.category_client import CategoryClient
from clients.spends_client import SpendsClient
from config import Settings
from databases.spend_db import SpendDb
from utils.sessions import BaseSession

logger = logging.getLogger(__name__)
fake = Faker()


@pytest.fixture(scope="session")
def base_session(settings: Settings, auth_token: str) -> BaseSession:
    return BaseSession(gateway_url=settings.GATEWAY_URL, token=auth_token)


@pytest.fixture(scope="session")
def spend_db(settings) -> SpendDb:
    return SpendDb(settings.SPEND_DB_URL)


@pytest.fixture(scope="session")
def category_client(base_session: BaseSession) -> CategoryClient:
    return CategoryClient(session=base_session)


@pytest.fixture(scope="session")
def spends_client(base_session: BaseSession) -> SpendsClient:
    return SpendsClient(session=base_session)


@pytest.fixture
def user_with_category_slots(category_client, user_credentials):
    """Подготовить пользователя с доступными слотами для категорий."""
    username = user_credentials.username

    yield username


def _cleanup_test_data(settings, username: str):
    import allure
    from allure_commons.types import AttachmentType

    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.SPEND_DB_URL)

        with engine.connect() as conn:
            result_spends = conn.execute(
                text("DELETE FROM spend WHERE username = :username"),
                {"username": username}
            )

            # Удалить ВСЕ категории для конкретного пользователя
            result_cats = conn.execute(
                text("DELETE FROM category WHERE username = :username"),
                {"username": username}
            )

            conn.commit()
            if result_spends.rowcount > 0 or result_cats.rowcount > 0:
                cleanup_msg = f"Очистка для {username}: удалено {result_spends.rowcount} трат и {result_cats.rowcount} категорий"
                logging.info(cleanup_msg)
                allure.attach(
                    cleanup_msg,
                    name="Результат очистки тестовых данных",
                    attachment_type=AttachmentType.TEXT
                )
    except Exception as e:
        error_msg = f"Ошибка при очистке для {username}: {str(e)}"
        logging.warning(error_msg)
        allure.attach(
            error_msg,
            name="Ошибка очистки",
            attachment_type=AttachmentType.TEXT
        )


@pytest.fixture(autouse=True, scope="function")
def test_cleanup(settings, user_credentials):
    yield
    
    with allure.step(f"Финальная очистка данных для {user_credentials.username}"):
        _cleanup_test_data(settings, user_credentials.username)
