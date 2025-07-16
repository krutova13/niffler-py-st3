from requests import Response

from clients.api_client import ApiClient


class CategoryClient(ApiClient):

    def __init__(self, env: str, token: str):
        super().__init__(env, token)

    def create_category(self, category: str) -> Response:
        test_data: dict = {"name": category}
        return self.session.post("/api/categories/add", json=test_data)

    def get_categories(self) -> Response:
        return self.session.get("/api/categories/all")
