import uuid
from datetime import datetime

import allure
import pytest
import requests


@allure.epic("Приложение Niffler")
@allure.feature("Управление категориями")
@allure.tag("api", "rest")
@pytest.mark.api
class TestCategoryAPI:
    @allure.title("Создание новой категории - базовая валидация")
    @allure.description("Проверка создания категории с корректными данными")
    def test_create_category_basic(self, category_client, verify):
        category_name = f"ТестоваяКатегория_{uuid.uuid4().hex[:6]}_{datetime.now().timestamp()}"

        response = category_client.add_category(name=category_name)
        verify.category_structure(response)
        assert response.name == category_name, f"Имя категории не совпадает: ожидалось {category_name}, получено {response.name}"
        assert response.archived is False, "Новая категория не должна быть архивной"

    @allure.title("Создание категории для пользователя")
    @allure.description("Проверка создания категории с контекстом пользователя")
    def test_create_category_for_user(self, category_client, user_with_category_slots, verify):
        category_name = f"КатегорияПользователя_{uuid.uuid4().hex[:6]}"

        try:
            response = category_client.add_category(name=category_name)
            verify.category_structure(response)
            assert response.name == category_name
            if hasattr(response, 'username'):
                assert response.username == user_with_category_slots
        except ValueError as e:
            if "over than 8 categories" in str(e):
                pytest.skip("У пользователя уже максимум 8 категорий - невозможно добавить еще")
            raise

    @allure.title("Получение всех категорий - валидация структуры")
    @allure.description("Проверка корректности структуры возвращаемых категорий")
    def test_get_all_categories(self, category_client, verify):
        categories = category_client.get_categories()

        assert isinstance(categories, list), "Категории должны возвращаться списком"
        for category in categories[:3]:
            verify.category_structure(category)

    @allure.title("Обновление категории - изменение имени")
    @allure.description("Проверка возможности изменения имени существующей категории")
    def test_update_category_name(self, category_client, user_with_category_slots, verify):
        category = category_client.add_category(name=f"Исходная_{uuid.uuid4().hex[:4]}")
        new_name = f"Обновленная_{uuid.uuid4().hex[:4]}"

        updated = category_client.update_category({
            "id": str(category.id),
            "name": new_name,
            "username": user_with_category_slots,
            "archived": False
        })

        verify.category_structure(updated)
        assert updated.name == new_name, f"Имя не обновилось: ожидалось {new_name}, получено {updated.name}"
        assert str(updated.id) == str(category.id), "ID категории не должен измениться"

    @allure.title("Негативные тесты - некорректные имена категорий")
    @allure.description("Проверка валидации некорректных имен категорий")
    @pytest.mark.parametrize("invalid_name,expected_error", [
        ("", "Category can not be blank"),
        ("   ", "Category can not be blank"),  # Только пробелы
        ("X" * 51, "Allowed category length"),
    ])
    def test_invalid_category_names(self, category_client, invalid_name, expected_error, verify):
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            category_client.add_category(name=invalid_name)

        assert exc_info.value.response.status_code == 400, "Ожидается код ошибки 400"
        error_detail = exc_info.value.response.json().get("detail", "")
        assert expected_error in error_detail, f"Ожидалось '{expected_error}' в '{error_detail}'"

    @allure.title("Жизненный цикл архивации категории")
    @allure.description("Проверка возможности архивации и разархивации категории")
    def test_archive_category(self, category_client, user_with_category_slots, verify):
        category = category_client.add_category(name=f"ДляАрхивации_{uuid.uuid4().hex[:4]}")

        archived = category_client.update_category({
            "id": str(category.id),
            "name": category.name,
            "username": user_with_category_slots,
            "archived": True
        })

        verify.category_structure(archived)
        assert archived.archived is True, "Категория должна быть архивной"
        assert str(archived.id) == str(category.id), "ID категории не должен измениться"

    @allure.title("Обновление несуществующей категории")
    @allure.description("Проверка обработки попытки обновления несуществующей категории")
    def test_update_nonexistent_category(self, category_client, verify):
        fake_id = str(uuid.uuid4())

        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            category_client.update_category({
                "id": fake_id,
                "name": "Призрак",
                "username": "test_user",
                "archived": False
            })

        assert exc_info.value.response.status_code == 404, "Ожидается код ошибки 404"
        assert "not found" in exc_info.value.response.text.lower(), "Ожидается сообщение о том, что категория не найдена"
