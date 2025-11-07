import pytest
from databases.userdata_db import UserdataDB
from faker import Faker

from clients.soap_client import SoapClient
from models.enums import Currency
from models.user import UserData


@pytest.fixture
def soap_client() -> SoapClient:
    return SoapClient()


@pytest.fixture
def userdata_db(settings) -> UserdataDB:
    return UserdataDB(settings.USER_DB_URL)


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def user_with_id() -> str:
    return "qwerty"


@pytest.fixture
def user_without_id() -> str:
    return "test_user"


@pytest.fixture
def soap_user(user_with_id: str) -> str:
    return user_with_id


@pytest.fixture
def soap_friends_user(user_with_id: str) -> str:
    return user_with_id


@pytest.fixture
def soap_actions_user(user_with_id: str) -> str:
    return user_with_id


@pytest.fixture
def soap_friend_user(user_without_id: str) -> str:
    return user_without_id


@pytest.fixture
def mock_users(faker: Faker) -> list[UserData]:
    return [
        UserData(
            id=faker.uuid4(),
            username=faker.user_name(),
            currency=Currency.RUB
        ) for _ in range(5)
    ]


@pytest.fixture
def mock_friends(faker: Faker) -> list[UserData]:
    return [
        UserData(
            id=faker.uuid4(),
            username=f"friend_{i}",
            currency=Currency.RUB
        ) for i in range(3)
    ]


@pytest.fixture
def mock_friends_actions(faker: Faker) -> list[UserData]:
    return [
        UserData(
            id=faker.uuid4(),
            username=f"action_friend_{i}",
            currency=Currency.RUB
        ) for i in range(5)
    ]


@pytest.fixture
def existing_soap_users(soap_client: SoapClient) -> list[str]:
    test_usernames = ["test_user", "qwerty", "user1"]

    existing_users = []
    for username in test_usernames:
        user_data, status = soap_client.get_current_user(username)
        if status == 200:
            existing_users.append(username)

    if len(existing_users) < 2:
        pytest.skip("Need at least 2 existing users in system for friendship tests")

    return existing_users


@pytest.fixture
def soap_actions_user(existing_soap_users: list[str]) -> str:
    return existing_soap_users[0]


@pytest.fixture
def soap_friend_user(existing_soap_users: list[str]) -> str:
    return existing_soap_users[1]


@pytest.fixture(autouse=True)
def cleanup():
    yield
