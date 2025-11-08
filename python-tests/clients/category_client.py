import json
import logging

import allure
from allure_commons.types import AttachmentType

from utils.sessions import BaseSession


class CategoryClient:
    session: BaseSession

    def __init__(self, session: BaseSession):
        self.session = session

    @allure.step("[API] Получить все категории")
    def get_categories(self):
        response = self.session.get("/api/categories/all")
        from models.category import CategoryGetResponse

        categories = [CategoryGetResponse.model_validate(item) for item in response.json()]

        allure.attach(
            json.dumps([c.model_dump() for c in categories], indent=2, ensure_ascii=False),
            name=f"Категории (всего: {len(categories)})",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Получено категорий: {len(categories)}")

        return categories

    @allure.step("[API] Добавить категорию '{name}'")
    def add_category(self, name: str):
        request_data = {"name": name}

        allure.attach(
            json.dumps(request_data, indent=2, ensure_ascii=False),
            name="Данные новой категории",
            attachment_type=AttachmentType.JSON
        )

        response = self.session.post("/api/categories/add", json=request_data)

        response_data = response.json()
        if isinstance(response_data, dict) and "detail" in response_data:
            error_msg = f"Не удалось добавить категорию '{name}': {response_data.get('detail')}"
            logging.warning(error_msg)
            allure.attach(error_msg, name="Ошибка добавления категории", attachment_type=AttachmentType.TEXT)
            raise ValueError(f"Ошибка создания категории: {response_data.get('detail')}")

        from models.category import CategoryGetResponse
        category = CategoryGetResponse.model_validate(response_data)

        allure.attach(
            json.dumps(category.model_dump(), indent=2, ensure_ascii=False),
            name=f"Созданная категория",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Категория создана: {name} (ID: {category.id})")

        return category

    @allure.step("[API] Обновить категорию")
    def update_category(self, category_data: dict):
        allure.attach(
            json.dumps(category_data, indent=2, ensure_ascii=False),
            name="Данные для обновления категории",
            attachment_type=AttachmentType.JSON
        )

        response = self.session.patch("/api/categories/update", json=category_data)

        from models.category import CategoryGetResponse
        updated_category = CategoryGetResponse.model_validate(response.json())

        allure.attach(
            json.dumps(updated_category.model_dump(), indent=2, ensure_ascii=False),
            name="Обновленная категория",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Категория обновлена: {updated_category.name} (ID: {updated_category.id})")

        return updated_category
