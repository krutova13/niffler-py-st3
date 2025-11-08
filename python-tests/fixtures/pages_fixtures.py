import pytest

from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.people_page import PeoplePage
from pages.profile_page import ProfilePage
from pages.spending.add_spending_page import AddSpendingPage
from pages.spending.edit_spending_page import EditSpendingPage


@pytest.fixture(scope="function")
def auth_page(auth_context):
    """Page with authenticated context for UI tests (new page for each test)."""
    page = auth_context.new_page()
    yield page
    # Close page after test if not already closed
    try:
        if not page.is_closed():
            page.close()
    except Exception:
        pass  # Page might already be closed


@pytest.fixture
def login_page(configs, page) -> LoginPage:
    return LoginPage(page, configs.FRONTEND_URL)


@pytest.fixture
def logout_page(configs, auth_page) -> LoginPage:
    return LoginPage(auth_page, configs.FRONTEND_URL)


@pytest.fixture
def main_page(configs, auth_page):
    page_obj = MainPage(auth_page, configs.FRONTEND_URL)
    page_obj.goto()
    return page_obj


@pytest.fixture
def profile_page(configs, auth_page):
    return ProfilePage(auth_page, configs.FRONTEND_URL)


@pytest.fixture
def people_page(configs, auth_page):
    return PeoplePage(auth_page, configs.FRONTEND_URL)


@pytest.fixture
def add_spending_page(configs, auth_page):
    return AddSpendingPage(auth_page, configs.FRONTEND_URL)


@pytest.fixture
def edit_spending_page(configs, auth_page):
    return EditSpendingPage(auth_page, configs.FRONTEND_URL)
