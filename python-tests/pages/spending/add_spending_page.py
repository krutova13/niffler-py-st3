from playwright.sync_api import Locator

from pages.spending.spending_form_page import SpendingFormPage


class AddSpendingPage(SpendingFormPage):
    URL: str = "/spending"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.title: Locator = page.locator('h2:has-text("Add new spending")')

    def goto(self):
        self.page.goto(f"{self.base_url}{self.URL}")
