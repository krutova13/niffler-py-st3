from requests import Response

from clients.api_client import ApiClient
from models.spend_create_request import SpendRequest


class SpendClient(ApiClient):

    def __init__(self, env: str, token: str):
        super().__init__(env, token)

    def create_spend(self, spend: SpendRequest) -> Response:
        return self.session.post("/api/spends/add", json=spend.model_dump())

    def delete_spend(self, spend_id: str) -> Response:
        url = f"/api/spends/remove?ids={spend_id}"
        return self.session.delete(url)
