from playwright.sync_api import Locator

from pages.spending.spending_form_page import SpendingFormPage


class AddSpendingPage(SpendingFormPage):
    URL: str = "/spending"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.title: Locator = page.locator('h2:has-text("Add new spending")')
        # self.currency_select: Locator = page.locator('div#currency')
        # self.currency_native_input: Locator = page.locator('input[name="currency"]')
        # self.category_input: Locator = page.locator('input#category')
        # self.category_options: Locator = page.locator('ul[role="listbox"] li[role="menuitem"]')
        # self.date_input: Locator = page.locator('input[name="date"]')
        # self.date_picker_btn: Locator = page.locator('button[aria-label^="Choose date"]')
        # self.description_input: Locator = page.locator('input#description')
        # self.cancel_btn: Locator = page.locator('button#cancel')
        # self.save_btn: Locator = page.locator('button#save')
        # self.edit_spending_btns: Locator = page.locator('button[aria-label="Edit spending"]')

    def goto(self):
        self.page.goto(f"{self.base_url}{self.URL}")

    # def fill_amount(self, amount: str):
    #     self.amount_input.fill(amount)
    #
    # def select_currency(self, currency: str):
    #     self.currency_select.click()
    #     self.page.locator(f'li[role="option"]:has-text("{currency}")').click()
    #
    # def fill_category(self, category: str):
    #     self.category_input.fill(category)
    #     option = self.category_options.filter(has_text=category)
    #     if option.count() > 0:
    #         option.first.click()
    #
    # def fill_date(self, date: str):
    #     self.date_input.fill(date)
    #
    # def fill_description(self, description: str):
    #     self.description_input.fill(description)
    #
    # def save(self):
    #     self.save_btn.click()
    #
    # def cancel(self):
    #     self.cancel_btn.click()
