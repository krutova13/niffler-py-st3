from playwright.sync_api import Locator

from pages.base_page import BasePage


class SpendingFormPage(BasePage):
    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.amount_input: Locator = page.locator('input#amount')
        self.currency_dropdown: Locator = page.locator('div[role="combobox"][id="currency"]')
        self.currency_option: Locator = page.locator('ul[role="listbox"] li[role="option"]')
        self.category_input: Locator = page.locator('input#category')
        self.category_options: Locator = page.locator('ul[role="listbox"] li[role="menuitem"]')
        self.date_input: Locator = page.locator('input[name="date"]')
        self.date_picker_btn: Locator = page.locator('button[aria-label^="Choose date"]')
        self.description_input: Locator = page.locator('input#description')
        self.cancel_btn: Locator = page.locator('button#cancel')
        self.save_btn: Locator = page.locator('button#save')

    def fill_amount(self, amount: str):
        self.amount_input.fill(amount)

    def select_currency(self, currency_code: str):
        self.currency_dropdown.click()
        self.currency_option.filter(has_text=currency_code).first.click()

    def fill_category(self, category: str):
        self.category_input.fill(category)
        option = self.category_options.filter(has_text=category)
        if option.count() > 0:
            option.first.click()

    def fill_date(self, date: str):
        self.date_input.fill(date)

    def fill_description(self, description: str):
        self.description_input.fill(description)

    def save(self):
        self.save_btn.click()

    def cancel(self):
        self.cancel_btn.click()
