from requests import Response

from config.config import Server
from session.base_session import BaseSession


class AuthClient:

    def __init__(self, env):
        self.session = BaseSession(base_url=Server(env).base_auth_url)

    def get_xsrf_token(self) -> str:
        response = self.session.get("/register")
        return response.headers.get("X-XSRF-TOKEN")

    def register(self, username: str, password: str, xsrf_token: str) -> Response:
        data = {
            "_csrf": xsrf_token,
            "username": username,
            "password": password,
            "passwordSubmit": password,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"XSRF-TOKEN={xsrf_token}",
        }
        response = self.session.post("/register", data=data, headers=headers)
        return response
