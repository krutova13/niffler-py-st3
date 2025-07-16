import pytest

from marks import Pages
from pages.login_page import LoginPage
from pages.main_page import MainPage


@pytest.mark.usefixtures("register")
def test_login_success(page_factory, auth_url, test_user: tuple):
    username, password = test_user
    login_page: LoginPage = page_factory(LoginPage, auth_url)
    login_page.goto()
    login_page.login(username, password)
    main_page: MainPage = page_factory(MainPage)
    assert main_page.header.is_title_visible()


def test_login_failure(page_factory, auth_url, test_user: tuple):
    username, _ = test_user
    login_page = page_factory(LoginPage, auth_url)
    login_page.goto()
    login_page.login(username, "wrong_password")
    assert login_page.is_error_visible()


@Pages.main_page
def test_logout(page_factory, auth_url, main_page):
    main_page.sigh_out()
    login_page: LoginPage = page_factory(LoginPage, auth_url)
    assert login_page.is_header_visible()
