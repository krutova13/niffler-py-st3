from playwright.sync_api import Locator

from pages.spending.spending_form_page import SpendingFormPage


class EditSpendingPage(SpendingFormPage):

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.title: Locator = page.locator('h2:has-text("Edit spending")')

    def goto(self, spend_id: str):
        self.page.goto(f"{self.base_url}/spending/{spend_id}")
