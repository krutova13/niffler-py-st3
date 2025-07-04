from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.components.delete_dialog import DeleteDialog
from pages.components.header import Header


class MainPage(BasePage):
    URL: str = "/main"
    RUB_SYMBOL = "₽"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.header = Header(page)
        self.delete_dialog = DeleteDialog(page)
        self.delete_btn: Locator = page.locator('button#delete')
        self.search_input: Locator = page.locator('input[aria-label="search"]')
        self.clear_button = page.locator('button#input-clear')
        self.checkbox_cells: Locator = page.locator('input[type="checkbox"]')
        self.next_btn: Locator = page.locator('button#page-next')
        self.prev_btn: Locator = page.locator('button#page-prev')
        self.no_spendings_text: Locator = page.locator('p:has-text("There are no spendings")')
        self.no_spendings_img: Locator = page.locator('img[alt="Lonely niffler"]')
        self.edit_spending_btns: Locator = page.locator('button[aria-label="Edit spending"]')
        self.table_rows = page.locator('tbody tr')
        self.row_checkboxes = page.locator('tbody input[type="checkbox"]')
        self.category_cells = page.locator('td.css-18x39oq')
        self.amount_cells = page.locator('td.css-1snpvth')
        self.description_cells = page.locator('td.css-1delpu4')
        self.date_cells = page.locator('td.css-s5nwpc')

    def goto(self):
        self.page.goto(f"{self.base_url}{self.URL}")

    def open_profile(self):
        self.header.open_profile()

    def create_new_spending(self):
        self.header.click_new_spending()

    def search(self, text: str):
        self.search_input.fill(text)
        self.search_input.press("Enter")

    def clear_search(self):
        self.clear_button.click()

    def select_all_spendings(self):
        self.checkbox_cells.nth(0).check()

    def select_last_spending(self):
        self.checkbox_cells.nth(-1).check()

    def delete_selected(self):
        self.delete_btn.click()

    def confirm_delete(self):
        self.delete_dialog.confirm()

    def edit_spending(self):
        self.edit_spending_btns.last.click()

    def is_no_spendings_placeholder_visible(self) -> bool:
        self.no_spendings_img.wait_for(timeout=3000)
        return self.no_spendings_text.is_visible() and self.no_spendings_img.is_visible()

    def is_last_spending_date(self, expected: str) -> bool:
        return _is_last_spending_entity(self.date_cells, expected)

    def is_last_spending_description(self, expected: str) -> bool:
        return _is_last_spending_entity(self.description_cells, expected)

    def is_last_spending_category(self, expected: str) -> bool:
        return _is_last_spending_entity(self.category_cells, expected)

    def is_last_spending_amount(self, expected: str, currency: str = RUB_SYMBOL) -> bool:
        self.amount_cells.first.wait_for(timeout=3000)
        amounts: list[str] = self.amount_cells.all_inner_texts()
        formatted_expected: str = _format_amount(expected)
        return amounts and amounts[-1] == f"{formatted_expected} {currency}"


def _format_amount(amount: str) -> str:
    try:
        f = float(amount)
        if f.is_integer():
            return str(int(f))
        return str(amount)
    except Exception:
        return str(amount)


def _is_last_spending_entity(entity: Locator, expected: str) -> bool:
    entity.first.wait_for(timeout=3000)
    entities: list[str] = entity.all_inner_texts()
    return entities and entities[-1] == expected
