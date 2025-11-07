from http import HTTPStatus
from urllib.parse import parse_qs, urlparse, urljoin

import requests
from requests import Session, Response

from utils.allure_helpers import allure_attach_request


def raise_for_status(function):
    def wrapper(*args, **kwargs):
        response = function(*args, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == HTTPStatus.BAD_REQUEST:
                error_msg = f"{e}\nОтвет сервера: {response.text}"
                raise requests.HTTPError(error_msg, response=response) from e
            raise

        try:
            json_data = response.json()
            if isinstance(json_data, dict) and json_data.get('type', '').startswith('niffler-'):
                status_code = json_data.get('status', 500)
                error_msg = json_data.get('detail', 'Неизвестная ошибка')

                response.status_code = status_code
                error = requests.HTTPError(f"{status_code} Ошибка: {error_msg}", response=response)
                raise error
        except (ValueError, AttributeError):
            pass

        return response

    return wrapper


class BaseSession(Session):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.gateway_url = kwargs.pop("gateway_url", None)
        self.token = kwargs.get("token", None)
        self.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    @raise_for_status
    @allure_attach_request
    def request(self, method: str, path: str, check_status: bool = True, **kwargs) -> Response:
        return super().request(method, urljoin(str(self.gateway_url), path), **kwargs)


class AuthSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.pop("base_url", "")
        self.code = None

    @raise_for_status
    @allure_attach_request
    def request(self, method, url, **kwargs):
        response = super().request(method, self.base_url + url, **kwargs)

        for r in response.history:
            cookies = r.cookies.get_dict()
            self.cookies.update(cookies)
            location = r.headers.get("Location")
            if location:
                code = parse_qs(urlparse(location).query).get("code", None)
                if code:
                    self.code = code[0]

        if hasattr(response, 'url') and response.url:
            code = parse_qs(urlparse(response.url).query).get("code", None)
            if code:
                self.code = code[0]

        return response
