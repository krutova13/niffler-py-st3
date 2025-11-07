import json
import logging

import allure
from allure_commons.types import AttachmentType

from utils.sessions import BaseSession


class SpendsClient:
    session: BaseSession

    def __init__(self, session: BaseSession):
        self.session = session

    @allure.step('[API] Получить список трат: валюта={filter_currency}, период={filter_period}')
    def get_spends(self, filter_currency: str = None, filter_period: str = None):
        params = {"filterCurrency": filter_currency, "filterPeriod": filter_period}

        allure.attach(
            json.dumps(params, indent=2, ensure_ascii=False),
            name="Параметры фильтрации",
            attachment_type=AttachmentType.JSON
        )

        response = self.session.get("/api/spends/all", params=params)
        from models.spend import SpendResponse

        spends = [SpendResponse.model_validate(item) for item in response.json()]

        allure.attach(
            json.dumps([s.model_dump() for s in spends], indent=2, ensure_ascii=False, default=str),
            name=f"Траты (всего: {len(spends)})",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Получено трат: {len(spends)}")

        return spends

    @allure.step('[API] Получить трату по ID: {spend_id}')
    def get_spend_by_id(self, spend_id: str):
        response = self.session.get(f"/api/spends/{spend_id}")
        from models.spend import SpendResponse

        spend = SpendResponse.model_validate(response.json())

        allure.attach(
            json.dumps(spend.model_dump(), indent=2, ensure_ascii=False, default=str),
            name=f"ID траты: {spend_id}",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Получена трата: {spend_id}")

        return spend

    @allure.step('[API] Добавить трату')
    def add_spends(self, spend):
        spend_data = spend.model_dump() if hasattr(spend, 'model_dump') else spend

        allure.attach(
            json.dumps(spend_data, indent=2, ensure_ascii=False, default=str),
            name="Данные новой траты",
            attachment_type=AttachmentType.JSON
        )

        response = self.session.post("/api/spends/add", json=spend_data)
        from models.spend import SpendResponse

        created_spend = SpendResponse.model_validate(response.json())

        allure.attach(
            json.dumps(created_spend.model_dump(), indent=2, ensure_ascii=False, default=str),
            name=f"Созданная трата (ID: {created_spend.id})",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Трата создана: {created_spend.id}")

        return created_spend

    @allure.step('[API] Обновить трату')
    def edit_spend(self, spend_data):
        data = spend_data.model_dump() if hasattr(spend_data, 'model_dump') else spend_data

        allure.attach(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            name="Данные для обновления траты",
            attachment_type=AttachmentType.JSON
        )

        response = self.session.patch("/api/spends/edit", json=data)
        from models.spend import SpendResponse

        updated_spend = SpendResponse.model_validate(response.json())

        allure.attach(
            json.dumps(updated_spend.model_dump(), indent=2, ensure_ascii=False, default=str),
            name=f"Обновленная трата (ID: {updated_spend.id})",
            attachment_type=AttachmentType.JSON
        )
        logging.info(f"Трата обновлена: {updated_spend.id}")

        return updated_spend

    @allure.step('[API] Удалить траты: {ids}')
    def delete_spends(self, ids: list[str]):
        allure.attach(
            json.dumps(ids, indent=2, ensure_ascii=False),
            name=f"ID трат для удаления (всего: {len(ids)})",
            attachment_type=AttachmentType.JSON
        )

        self.session.delete("/api/spends/remove", params={"ids": ids})

        logging.info(f"Удалено трат: {len(ids)}")
        allure.attach(
            f"Успешно удалено {len(ids)} трат(ы)",
            name="Результат удаления",
            attachment_type=AttachmentType.TEXT
        )
