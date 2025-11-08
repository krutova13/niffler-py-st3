import json

import allure
import pytest
from allure_commons.types import AttachmentType

from clients.auth_client import AuthClient
from config import Settings
from models.user_credentials import UserCredentials
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def auth_token(settings: Settings, user_credentials: UserCredentials):
    return AuthClient(settings).get_token(user_credentials.username, user_credentials.password)


@pytest.fixture(scope="session", autouse=True)
def register(settings: Settings, user_credentials: UserCredentials):
    username, password = user_credentials.username, user_credentials.password
    api = AuthClient(settings)
    try:
        response = api.register(username, password)
    except Exception as e:
        if "400" in str(e) or "already exists" in str(e):
            response = None
        else:
            raise

    yield response

    api.session.close()


@pytest.fixture(scope="session")
def auth_storage_state(browser, configs, user_credentials: UserCredentials, storage_state_path: str):
    context = browser.new_context()
    page = context.new_page()

    login_page_local = LoginPage(page, configs.FRONTEND_URL)
    login_page_local.goto()
    login_page_local.login(user_credentials.username, user_credentials.password)
    token = login_page_local.get_id_token()

    context.storage_state(path=storage_state_path)
    context.close()

    return storage_state_path


@pytest.fixture(scope="session")
def auth(auth_storage_state: str) -> str:
    with open(auth_storage_state, 'r') as f:
        state = json.load(f)

    token = None
    for item in state.get("origins", []):
        for kv in item.get("localStorage", []):
            if kv.get("name") == "id_token":
                token = kv.get("value")
                break
        if token:
            break

    if token:
        allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
        return token
    else:
        raise RuntimeError("id_token not found in storage_state")


@pytest.fixture(scope="session")
def auth_context(browser, auth_storage_state: str):
    context = browser.new_context(storage_state=auth_storage_state)
    yield context
    context.close()


@pytest.fixture(scope="session")
def storage_state_path(tmp_path_factory, worker_id) -> str:
    filename = f"auth_{worker_id}.json"
    return str(tmp_path_factory.mktemp("state") / filename)


@pytest.fixture(scope="session")
def user_credentials(settings, worker_id) -> UserCredentials:
    if worker_id != 'master':
        username = f"{settings.TEST_USERNAME}_{worker_id}"
    else:
        username = settings.TEST_USERNAME

    creds = UserCredentials(username=username, password=settings.TEST_PASSWORD)
    creds_payload = {
        "username": creds.username,
        "password": creds.password,
        "worker_id": worker_id
    }
    allure.attach(json.dumps(creds_payload, indent=2),
                  name="credentials.json",
                  attachment_type=AttachmentType.JSON)

    return creds


@pytest.fixture(scope="session")
def auth_client(settings: Settings):
    return AuthClient(settings)
