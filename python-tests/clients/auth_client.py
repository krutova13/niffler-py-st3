import base64

import allure
import pkce
import requests
from allure_commons.types import AttachmentType

from config import Settings
from models.oauth import OAuthRequest
from utils.sessions import AuthSession


class AuthClient:
    def __init__(self, settings: Settings):
        self.session = AuthSession(base_url=settings.AUTH_URL)
        self.redirect_uri = settings.FRONTEND_URL + "/authorized"
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()

        auth_string = f"client:{settings.AUTH_SECRET}"
        self._basic_token = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        self.authorization_basic = {"Authorization": f"Basic {self._basic_token}"}
        self.token = None

    @allure.step("[Auth] Зарегистрировать пользователя '{username}'")
    def register(self, username: str, password: str) -> requests.Response:
        self.session.get(
            url='/register',
            params={
                'redirect_uri': self.redirect_uri
            },
            allow_redirects=True
        )
        result = self.session.post(
            url='/register',
            data={
                "username": username,
                "password": password,
                "passwordSubmit": password,
                "_csrf": self.session.cookies.get("XSRF-TOKEN")
            },
            allow_redirects=True
        )

        allure.attach(
            f"Пользователь: {username}\nСтатус: {result.status_code}",
            name="Результат регистрации",
            attachment_type=AttachmentType.TEXT
        )

        return result

    @allure.step("[Auth] Получить токен для пользователя '{username}'")
    def get_token(self, username: str, password: str) -> str:
        with allure.step("Инициировать OAuth2 авторизацию"):
            self.session.get(
                url="/oauth2/authorize",
                params=OAuthRequest(
                    redirect_uri=self.redirect_uri,
                    code_challenge=self.code_challenge
                ).model_dump(),
                allow_redirects=True
            )

        xsrf_tokens = [cookie.value for cookie in self.session.cookies if cookie.name == "XSRF-TOKEN"]
        xsrf_token = xsrf_tokens[-1] if xsrf_tokens else None

        with allure.step("Выполнить вход"):
            login_response = self.session.post(
                url="/login",
                data={
                    "username": username,
                    "password": password,
                    "_csrf": xsrf_token
                },
                allow_redirects=True
            )

            if "error" in login_response.url and login_response.status_code == 200:
                error_msg = f"Ошибка входа. URL: {login_response.url}"
                allure.attach(error_msg, name="Ошибка входа", attachment_type=AttachmentType.TEXT)
                raise ValueError(error_msg)

        with allure.step("Получить код авторизации"):
            auth_response = self.session.get(
                url="/oauth2/authorize",
                params=OAuthRequest(
                    redirect_uri=self.redirect_uri,
                    code_challenge=self.code_challenge
                ).model_dump(),
                allow_redirects=True
            )

            if not self.session.code:
                error_msg = f"Код авторизации не получен. URL: {auth_response.url}"
                allure.attach(error_msg, name="Ошибка получения кода", attachment_type=AttachmentType.TEXT)
                raise ValueError(error_msg)

        with allure.step("Обменять код на токен"):
            token_data = {
                "code": self.session.code,
                "redirect_uri": self.redirect_uri,
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "client_id": "client"
            }

            token_response = self.session.post(
                url="/oauth2/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            token_json = token_response.json()
            self.token = token_json.get("access_token")
            if not self.token:
                error_msg = f"Не удалось получить токен. Ошибка: {token_json.get('error', 'Неизвестная')}"
                allure.attach(error_msg, name="Ошибка получения токена", attachment_type=AttachmentType.TEXT)
                raise ValueError(error_msg)

        allure.attach(
            f"Токен получен для пользователя: {username}",
            name="Успешная авторизация",
            attachment_type=AttachmentType.TEXT
        )

        return self.token

    def close(self):
        if self.session:
            self.session.close()
