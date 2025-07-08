import os

from requests import Response

from config.config import Server
from session.base_session import BaseSession


class ApiClient:
    def __init__(self, env):
        token = os.getenv("TOKEN")
        self.session = BaseSession(base_url=Server(env).base_api_url, token=token)

    def request(
            self,
            method: str,
            url: str,
            params: dict = None,
            body: dict = None,
            headers: dict = None,
            **kwargs
    ) -> Response:
        return self.session.request(
            method=method,
            url=url,
            params=params,
            json=body,
            headers=headers,
            **kwargs
        )
