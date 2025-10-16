import pytest

from marks import Pages


@pytest.mark.usefixtures("register")
def test_login_success(login_page, main_page, user_credentials):
    login_page.goto()
    login_page.login(user_credentials.username, user_credentials.password)
    assert main_page.header.is_title_visible()


def test_login_failure(login_page, user_credentials):
    login_page.goto()
    login_page.login(user_credentials.username, "wrong_password")
    assert login_page.is_error_visible()


@Pages.main_page
def test_logout(main_page, login_page_auth):
    main_page.sigh_out()
    assert login_page_auth.is_header_visible()
