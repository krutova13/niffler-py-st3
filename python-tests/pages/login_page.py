from playwright.sync_api import Locator

from pages.base_page import BasePage


class LoginPage(BasePage):
    URL: str = "/login"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.username_input: Locator = page.locator('input[name="username"]')
        self.password_input: Locator = page.locator('input[name="password"]')
        self.login_button: Locator = page.locator('button[type="submit"]')
        self.error_message: Locator = page.locator('.form__error-container .form__error')

    def goto(self):
        self.page.goto(f"{self.base_url}{self.URL}")

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def is_error_visible(self) -> bool:
        return self.error_message.is_visible()

    def get_error_text(self) -> str:
        return self.error_message.inner_text()
