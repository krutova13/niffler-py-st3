import os
from http import HTTPStatus

import allure
import dotenv
from allure_commons.types import AttachmentType

from clients.category_client import CategoryClient
from config.config import Config
from databases.spend_db import SpendDb
from models.category_get_response import CategoryGetResponse
from models.spend_create_request import SpendRequest
from models.user_credentials import UserCredentials
from pages.main_page import MainPage
from pages.people_page import PeoplePage
from pages.profile_page import ProfilePage
from pages.spending.add_spending_page import AddSpendingPage
from pages.spending.edit_spending_page import EditSpendingPage

dotenv.load_dotenv()

import pytest
from requests import Response
import json
from clients.auth_client import AuthClient
from clients.spend_client import SpendClient
from config.config_provider import ConfigProvider
from models.spend_create_response import SpendResponse, Category
from pages.login_page import LoginPage


def pytest_addoption(parser):
    parser.addoption("--env", default="dev")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def configs(env) -> Config:
    config_instance = Config(
        frontend_url=ConfigProvider(env).get(key="frontend_url"),
        gateway_url=ConfigProvider(env).get(key="gateway_url"),
        spend_db_url=ConfigProvider(env).get(key="spend_db_url")
    )
    allure.attach(config_instance.model_dump_json(indent=2), name="envs.json", attachment_type=AttachmentType.JSON)
    return config_instance


@pytest.fixture(scope="session")
def user_credentials() -> UserCredentials:
    return UserCredentials(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))


@pytest.fixture(scope="session", autouse=True)
def register(env, user_credentials: UserCredentials):
    username, password = user_credentials.username, user_credentials.password
    api = AuthClient(env)
    token: str = api.get_xsrf_token()
    response: Response = api.register(username, password, token)

    yield response

    api.session.close()


@pytest.fixture(scope="session")
def storage_state_path(tmp_path_factory) -> str:
    return str(tmp_path_factory.mktemp("state") / "auth.json")


@pytest.fixture(scope="session")
def auth_storage_state(browser, configs, user_credentials: UserCredentials, storage_state_path: str):
    context = browser.new_context()
    page = context.new_page()

    login_page_local = LoginPage(page, configs.frontend_url)
    login_page_local.goto()
    login_page_local.login(user_credentials.username, user_credentials.password)
    login_page_local.get_id_token()

    context.storage_state(path=storage_state_path)
    context.close()

    return storage_state_path


@pytest.fixture
def auth_context(browser, auth_storage_state: str):
    context = browser.new_context(storage_state=auth_storage_state)
    yield context
    context.close()


@pytest.fixture
def auth_page(auth_context):
    page = auth_context.new_page()
    yield page
    page.close()


@pytest.fixture
def login_page(configs, page) -> LoginPage:
    return LoginPage(page, configs.frontend_url)


@pytest.fixture
def logout_page(configs, auth_page) -> LoginPage:
    return LoginPage(auth_page, configs.frontend_url)


@pytest.fixture
def main_page(configs, auth_page):
    page_obj = MainPage(auth_page, configs.frontend_url)
    page_obj.goto()
    return page_obj


@pytest.fixture
def profile_page(configs, auth_page):
    return ProfilePage(auth_page, configs.frontend_url)


@pytest.fixture
def people_page(configs, auth_page):
    return PeoplePage(auth_page, configs.frontend_url)


@pytest.fixture
def add_spending_page(configs, auth_page):
    return AddSpendingPage(auth_page, configs.frontend_url)


@pytest.fixture
def edit_spending_page(configs, auth_page):
    return EditSpendingPage(auth_page, configs.frontend_url)


@pytest.fixture
def auth(auth_storage_state: str) -> str:
    with open(auth_storage_state, 'r') as f:
        state = json.load(f)
    for item in state.get("origins", []):
        for kv in item.get("localStorage", []):
            if kv.get("name") == "id_token":
                return kv.get("value")
    raise RuntimeError("id_token not found in storage_state")


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


@pytest.fixture(scope="session")
def spend_db(configs):
    return SpendDb(configs.spend_db_url)


@pytest.fixture(params=[])
def category_data(request, category_client) -> Category:
    category_name: str = request.param

    response: Response = category_client.get_categories()
    assert response.status_code == HTTPStatus.OK

    categories: list[CategoryGetResponse] = [CategoryGetResponse.model_validate(item) for item in response.json()]
    category = next((c for c in categories if c.name == category_name), None)

    if not category:
        create_resp = category_client.create_category(category_name)
        assert create_resp.status_code == HTTPStatus.OK
        category = Category.model_validate(create_resp.json())

    return category


@pytest.fixture
def test_category(spend_db, category_data: Category):
    yield category_data.name

    spend_db.delete_category(category_data.id)
    assert spend_db.get_category_by_id(category_data.id) is None


@pytest.fixture(params=[])
def test_spend(request, spends_client, spend_db):
    response: Response = spends_client.create_spend(request.getfixturevalue(request.param))
    assert response.status_code == HTTPStatus.CREATED
    spend_response: SpendResponse = SpendResponse.model_validate(response.json())

    yield spend_response

    spend_db.delete_spend(spend_response.id)
    spend_db.delete_category(spend_response.category.id)
    assert spend_db.get_spend_by_id(spend_response.id) is None


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
