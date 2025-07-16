import os
from http import HTTPStatus

import dotenv

from clients.category_client import CategoryClient
from models.category_get_response import CategoryGetResponse
from models.spend_create_request import SpendRequest
from pages.main_page import MainPage

dotenv.load_dotenv()

import pytest
from requests import Response
from clients.auth_client import AuthClient
from clients.spend_client import SpendClient
from config.config_provider import ConfigProvider
from models.spend_create_response import SpendResponse
from pages.base_page import BasePage
from pages.login_page import LoginPage


def pytest_addoption(parser):
    parser.addoption("--env", default="dev")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env):
    return ConfigProvider(env).get(key="base_ui_url")


@pytest.fixture(scope="session")
def frontend_url(env):
    return ConfigProvider(env).get(key="base_ui_url")


@pytest.fixture(scope="session")
def auth_url(env):
    return ConfigProvider(env).get(key="base_auth_url")


@pytest.fixture
def page_factory(page, base_url):
    def _factory(PageClass: type[BasePage], custom_url=None) -> BasePage:
        use_url = custom_url if custom_url is not None else base_url
        return PageClass(page, use_url)

    return _factory


@pytest.fixture(scope="session")
def test_user() -> tuple:
    return os.getenv("USERNAME"), os.getenv("PASSWORD")


@pytest.fixture(scope="session", autouse=True)
def register(env, test_user: tuple):
    username, password = test_user
    api = AuthClient(env)
    token: str = api.get_xsrf_token()
    response: Response = api.register(username, password, token)
    yield response
    api.session.close()


@pytest.fixture
def auth(page, register, page_factory, test_user: tuple) -> str:
    username, password = test_user
    login_page: LoginPage = page_factory(LoginPage, auth_url)
    login_page.goto()
    login_page.login(username, password)

    return login_page.get_id_token()


@pytest.fixture
def main_page(auth, page_factory, frontend_url):
    main_page: MainPage = page_factory(MainPage, frontend_url)
    main_page.goto()
    return main_page


@pytest.fixture
def spends_client(env, auth):
    api = SpendClient(env, auth)
    yield api
    api.session.close()


@pytest.fixture
def category_client(env, auth):
    api = CategoryClient(env, auth)
    yield api
    api.session.close()


@pytest.fixture(params=[])
def category_name(request, category_client) -> str:
    category_name: str = request.param
    response: Response = category_client.get_categories()
    assert response.status_code == HTTPStatus.OK
    categories: list[CategoryGetResponse] = [CategoryGetResponse.model_validate(item) for item in response.json()]
    category_names = [category.name for category in categories]
    if category_name not in category_names:
        category_client.create_category(category_name)
    return category_name


@pytest.fixture(params=[])
def spends(request, spends_client):
    response: Response = spends_client.create_spend(request.getfixturevalue(request.param))
    assert response.status_code == HTTPStatus.CREATED
    spend_response: SpendResponse = SpendResponse.model_validate(response.json())
    yield spend_response
    spends_client.delete_spend(spend_response.id)


@pytest.fixture
def spend_data() -> SpendRequest:
    return SpendRequest(
        amount="1000",
        description="test description",
        currency="RUB",
        spendDate="2025-07-01T20:32:03.698Z",
        category={
            "name": "Еда"
        }
    )
