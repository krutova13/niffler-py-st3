from pages.login_page import LoginPage
from pages.main_page import MainPage


def test_login_success(page_factory, test_user: dict):
    login_page: LoginPage = page_factory(LoginPage)
    login_page.goto()
    login_page.login(test_user.get("username"), test_user.get("password"))
    main_page: MainPage = page_factory(MainPage)
    assert main_page.header.is_title_visible()


def test_login_failure(page_factory, test_user: dict):
    login_page = page_factory(LoginPage)
    login_page.goto()
    login_page.login(test_user.get("username"), "wrong_password")
    assert login_page.is_error_visible()
