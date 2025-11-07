from typing import Generator

import pytest

from config import Settings
from databases.userdata_db import UserdataDB


@pytest.fixture
def users_db(settings: Settings) -> UserdataDB:
    return UserdataDB(settings.USER_DB_URL)


@pytest.fixture(autouse=True)
def clean_test_data(users_db: UserdataDB) -> Generator[list[str], None, None]:
    test_usernames: list[str] = []
    yield test_usernames

    if test_usernames:
        for username in test_usernames:
            try:
                if hasattr(users_db, 'delete_user'):
                    users_db.delete_user(username)
            except Exception as e:
                print(f"⚠️  Failed to clean user {username}: {e}")
