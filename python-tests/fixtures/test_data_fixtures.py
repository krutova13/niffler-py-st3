"""
Test data fixtures for API tests.
"""
import uuid

import pytest
from faker import Faker
from pytest import FixtureRequest

from models.category import Category
from models.spend import SpendRequest

fake = Faker()


@pytest.fixture
def spend_data() -> SpendRequest:
    return SpendRequest(
        amount="1000",
        description="test description",
        currency="RUB",
        spendDate="2025-07-01T20:32:03.698Z",
        category={
            "name": "Еда"
        }
    )


@pytest.fixture(params=[])
def category_data(request, category_client) -> Category:
    category_name: str = request.param

    categories = category_client.get_categories()
    category = next((c for c in categories if c.name == category_name), None)

    if not category:
        category = category_client.add_category(category_name)

    return category


@pytest.fixture
def test_category(spend_db, category_data: Category):
    import allure
    from allure_commons.types import AttachmentType
    
    yield category_data.name

    with allure.step(f"Удалить тестовую категорию: {category_data.name}"):
        spend_db.delete_category(category_data.id)
        deleted = spend_db.get_category_by_id(category_data.id)
        
        allure.attach(
            f"Категория удалена: {category_data.name} (ID: {category_data.id})",
            name="Очистка категории",
            attachment_type=AttachmentType.TEXT
        )
        
        assert deleted is None


@pytest.fixture(params=[])
def test_spend(request: FixtureRequest, spends_client, spend_db):
    import allure
    from allure_commons.types import AttachmentType
    
    spend_data = request.getfixturevalue(request.param)
    
    try:
        spend_response = spends_client.add_spends(spend_data)
    except Exception as e:
        if "over than 8 categories" in str(e) or (hasattr(e, 'response') and e.response.status_code == 406):
            pytest.skip("Пользователь имеет максимум 8 категорий - невозможно создать тестовую трату")
        raise

    yield spend_response

    with allure.step(f"Удалить тестовую трату: {spend_response.id}"):
        try:
            spend_db.delete_spend(spend_response.id)
            cleanup_msg = f"Трата удалена: {spend_response.id}"
            
            if hasattr(spend_response, 'category') and spend_response.category:
                spend_db.delete_category(str(spend_response.category.id))
                cleanup_msg += f"\nКатегория удалена: {spend_response.category.id}"
            
            allure.attach(
                cleanup_msg,
                name="Очистка траты",
                attachment_type=AttachmentType.TEXT
            )
        except Exception as e:
            allure.attach(
                f"Ошибка очистки траты: {str(e)}",
                name="Ошибка очистки",
                attachment_type=AttachmentType.TEXT
            )


@pytest.fixture
def random_username() -> str:
    return f"testuser_{uuid.uuid4().hex[:8]}"


class Verify:
    @staticmethod
    def category_structure(category):
        assert hasattr(category, 'id'), "Category should have 'id' field"
        assert hasattr(category, 'name'), "Category should have 'name' field"
        assert category.name, "Category name should not be empty"


@pytest.fixture
def verify():
    return Verify()
