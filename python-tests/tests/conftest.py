import os
from http import HTTPStatus
from typing import Type

import dotenv

dotenv.load_dotenv()

import pytest
from playwright.sync_api import Page, sync_playwright
from requests import Response

from clients.auth_client import AuthClient
from clients.spend_client import SpendClient
from config.config_provider import ConfigProvider
from models.spend_create_request import SpendRequest
from models.spend_create_response import SpendResponse
from pages.base_page import BasePage
from pages.login_page import LoginPage


@pytest.fixture(scope="function")
def page() -> Page:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


def pytest_addoption(parser):
    parser.addoption("--env", default="dev")


@pytest.fixture(scope="session")
def base_url(env):
    return ConfigProvider(env).get(key="base_ui_url")


@pytest.fixture
def page_factory(page, base_url):
    def _factory(PageClass: Type[BasePage]) -> BasePage:
        return PageClass(page, base_url)

    return _factory


@pytest.fixture(scope="session")
def test_user() -> dict:
    return {
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD")
    }


@pytest.fixture(scope="function")
def login(page_factory, test_user):
    login_page: LoginPage = page_factory(LoginPage)
    login_page.goto()
    login_page.login(test_user.get("username"), test_user.get("password"))
    yield test_user


@pytest.fixture(scope="session", autouse=True)
def register(env, test_user):
    api = AuthClient(env)
    token: str = api.get_xsrf_token()
    response: Response = api.register(
        test_user.get("username"),
        test_user.get("password"),
        token
    )
    yield response
    api.session.close()


@pytest.fixture(scope="function")
def spend_api(env):
    api = SpendClient(env)
    yield api
    api.session.close()


@pytest.fixture
def valid_spend() -> SpendRequest:
    return SpendRequest(
        amount="1000",
        description="",
        currency="RUB",
        spendDate="2025-07-01T20:32:03.698Z",
        category={
            "name": "Еда"
        }
    )


@pytest.fixture
def created_spend(spend_api, valid_spend):
    response: Response = spend_api.create_spend(valid_spend)
    assert response.status_code == HTTPStatus.CREATED
    spend_response: SpendResponse = SpendResponse.model_validate(response.json())
    yield spend_response
    spend_api.delete_spend(spend_response.id)
