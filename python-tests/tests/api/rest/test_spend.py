import logging
import uuid
from datetime import datetime, timedelta

import allure
import pytest

from clients.category_client import CategoryClient
from clients.spends_client import SpendsClient
from databases.spend_db import SpendDb
from models.spend import ErrorResponseModel, SpendModelAdd
from utils.allure_helpers import Epic, Feature, Story

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@allure.epic(Epic.api)
@allure.feature(Feature.spending)
@allure.tag("api", "rest", "spending")
@pytest.mark.api
class TestSpendAPI:
    @allure.title("Создание траты с различными сценариями")
    @allure.story(Story.api_crud)
    @pytest.mark.parametrize("test_data,expected_status,expected_error", [
        (
                {
                    "amount": 100.0,
                    "currency": "USD",
                    "spendDate": "2023-01-01",
                    "description": "Valid spend",
                    "category": {"name": "New Category"},
                },
                201,
                None
        ),
        (
                {
                    "amount": -100.0,
                    "currency": "USD",
                    "spendDate": "2023-01-03",
                    "description": "",
                    "category": {"name": ""},
                },
                400,
                "Amount should be greater than 0.01"
        ),
        (
                {
                    "amount": 0.01,
                    "currency": "USD",
                    "spendDate": "2023-01-01",
                    "description": "Min amount spend",
                    "category": {"name": "Boundary Check"},
                },
                201,
                None
        )
    ])
    def test_create_spend_with_model(self, random_username: str, test_data: dict[str, any],
                                     expected_status: int, expected_error: str, spends_client: SpendsClient):
        test_data["username"] = random_username
        spend_data = SpendModelAdd(**test_data)

        try:
            response = spends_client.add_spends(spend_data)

            if expected_status >= 400:
                assert isinstance(response, ErrorResponseModel)
                assert response.status == expected_status
                if expected_error:
                    assert expected_error in response.detail
            else:
                assert response.amount == test_data["amount"]
                assert response.currency == test_data["currency"]
                assert response.description == test_data["description"]
                assert response.category.name == test_data["category"]["name"]

        except Exception as e:
            if expected_status < 400:
                pytest.fail(f"Unexpected error: {str(e)}")
            elif expected_status == 400:
                if hasattr(e, 'response'):
                    error_data = e.response.json()
                    assert error_data.get('status') == 400
                    if expected_error:
                        assert expected_error in error_data.get('detail', '')
                else:
                    pytest.fail(f"Expected HTTP 400 error, got: {str(e)}")

    @allure.title("Получение траты по ID с валидацией данных")
    @allure.story(Story.api_crud)
    def test_get_spend_by_id(self, spends_client: SpendsClient, random_username: str):
        spend_data = SpendModelAdd(
            amount=150.0,
            currency="RUB",
            spendDate=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            description="Test get by ID",
            category={"name": "TestGetByID"},
            username=random_username
        )

        created_spend = spends_client.add_spends(spend_data)

        retrieved = spends_client.get_spend_by_id(created_spend.id)

        assert retrieved.id == created_spend.id
        assert float(retrieved.amount) == 150.0
        assert retrieved.currency == "RUB"
        assert retrieved.description == "Test get by ID"

        spends_client.delete_spends([str(retrieved.id)])

    @allure.title("Редактирование существующей траты с валидными данными")
    @allure.story(Story.api_crud)
    def test_edit_spend(self, spends_client: SpendsClient, random_username: str):
        spend_data = SpendModelAdd(
            amount=100.0,
            currency="USD",
            spendDate=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            description="Original spend",
            category={"name": "TestEdit"},
            username=random_username
        )

        created_spend = spends_client.add_spends(spend_data)

        updated_data = {
            "id": str(created_spend.id),
            "amount": 200.0,
            "currency": "EUR",
            "spendDate": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "description": "Updated spend",
            "category": {
                "id": str(created_spend.category.id),
                "name": created_spend.category.name
            },
            "username": random_username
        }

        updated_spend = spends_client.edit_spend(updated_data)

        assert updated_spend.id == created_spend.id
        assert float(updated_spend.amount) == 200.0
        assert updated_spend.description == "Updated spend"

        spends_client.delete_spends([str(updated_spend.id)])

    @allure.title("Тест создания траты с попыткой SQL injection")
    @allure.story(Story.boundary_tests)
    def test_sql_injection_attempt(self, spends_client: SpendsClient, random_username: str):
        malicious_data = {
            "amount": 100.0,
            "currency": "USD",
            "spendDate": "2023-01-01",
            "description": "'; DROP TABLE spends; --",
            "category": {"name": f"SQLTest_{uuid.uuid4().hex[:6]}"},
            "username": random_username
        }

        response = spends_client.add_spends(SpendModelAdd(**malicious_data))

        assert response.description == malicious_data["description"]
        assert "DROP TABLE" in response.description

        spends_client.delete_spends([str(response.id)])


@allure.epic(Epic.api)
@allure.feature(Feature.spending)
@allure.tag("api", "integration")
class TestIntegration:
    @allure.title("Полный пользовательский flow")
    @allure.story(Story.api_crud)
    def test_full_flow(
            self,
            category_client: CategoryClient,
            spends_client: SpendsClient,
            spend_db: SpendDb
    ):
        category_name = f"FlowCategory_{uuid.uuid4().hex[:6]}"
        category = category_client.add_category(name=category_name)

        spend_data = {
            "amount": 100.0,
            "currency": "USD",
            "spendDate": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "description": "Integration test",
            "category": {
                "id": str(category.id),
                "name": category.name
            },
            "username": "test_user"
        }
        spend = spends_client.add_spends(SpendModelAdd(**spend_data))

        retrieved = spends_client.get_spend_by_id(spend.id)
        assert retrieved.category.name == category.name

        spends_client.delete_spends([str(spend.id)])
        spend_db.delete_category(str(category.id))
