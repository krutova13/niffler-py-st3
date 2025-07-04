import logging

import curlify as curlify
from requests import Session


class BaseSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.get("base_url", None)
        self.token = kwargs.get("token", None)

    def request(self, method, url, headers=None, **kwargs):
        url = self.base_url + url
        headers = headers or {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = super().request(method, url, headers=headers, **kwargs)
        curl = curlify.to_curl(response.request)
        logging.info(curl)
        return response
