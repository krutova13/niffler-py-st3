import allure
import pytest

from marks import Pages
from utils.allure_helpers import Epic, Feature, Story


@allure.epic(Epic.ui)
@allure.feature(Feature.auth)
@allure.story(Story.user_management)
@allure.title("Успешный вход в систему")
@pytest.mark.usefixtures("register")
def test_login_success(login_page, main_page, user_credentials):
    login_page.goto()
    login_page.login(user_credentials.username, user_credentials.password)
    assert main_page.header.is_title_visible()


@allure.epic(Epic.ui)
@allure.feature(Feature.auth)
@allure.story(Story.user_management)
@allure.title("Неуспешный вход - неверный пароль")
def test_login_failure(login_page, user_credentials):
    login_page.goto()
    login_page.login(user_credentials.username, "wrong_password")
    assert login_page.is_error_visible()


@allure.epic(Epic.ui)
@allure.feature(Feature.auth)
@allure.story(Story.user_management)
@allure.title("Выход из системы")
@pytest.mark.usefixtures("register")
def test_logout(browser, configs, user_credentials):
    """Тест выхода из системы - использует отдельный контекст."""
    # Create separate context for logout test to not affect session auth_context
    context = browser.new_context()
    page = context.new_page()
    
    # Login first
    from pages.login_page import LoginPage
    from pages.main_page import MainPage
    
    login_page = LoginPage(page, configs.FRONTEND_URL)
    login_page.goto()
    login_page.login(user_credentials.username, user_credentials.password)
    
    main_page = MainPage(page, configs.FRONTEND_URL)
    page.wait_for_url(f"{configs.FRONTEND_URL}/main", timeout=5000)
    
    # Now logout
    main_page.sign_out()
    
    # Verify we're on login page
    assert login_page.is_header_visible()
    
    # Cleanup
    page.close()
    context.close()
