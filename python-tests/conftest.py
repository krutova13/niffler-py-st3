import os

import pytest
from dotenv import load_dotenv

from clients.kafka_client import KafkaClient
from config import Settings

pytest_plugins = [
    "fixtures.auth_fixtures",
    "fixtures.client_fixtures",
    "fixtures.grpc_fixtures",
    "fixtures.pages_fixtures",
    "fixtures.browser_fixtures",
    "fixtures.test_data_fixtures",
    "fixtures.allure_hooks",
    "fixtures.kafka_fixtures",
    "fixtures.soap_fixtures",
]


@pytest.fixture(scope="session")
def settings():
    load_dotenv()
    return Settings()


@pytest.fixture(scope="session")
def worker_id(request):
    if hasattr(request.config, 'workerinput'):
        return request.config.workerinput['workerid']
    return os.getenv('PYTEST_XDIST_WORKER', 'master')


@pytest.fixture(scope="session")
def auth_url(settings):
    return settings.AUTH_URL.rstrip('/')


@pytest.fixture(scope="session")
def frontend_url(settings):
    return settings.FRONTEND_URL.rstrip('/')


@pytest.fixture(scope="session")
def gateway_url(settings):
    return settings.GATEWAY_URL.rstrip('/')


@pytest.fixture(scope="session")
def configs(settings):
    return settings


@pytest.fixture(scope="session")
def kafka(settings):
    with KafkaClient(settings) as k:
        yield k


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
