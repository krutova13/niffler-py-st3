from playwright.sync_api import Locator

from pages.base_page import BasePage


class PeoplePage(BasePage):

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.tabs: Locator = page.locator('div[aria-label="People tabs"] a[role="tab"]')
        self.tab_friends: Locator = page.locator('a[role="tab"][href="/people/friends"]')
        self.tab_all_people: Locator = page.locator('a[role="tab"][href="/people/all"]')
        self.search_input: Locator = page.locator('input[placeholder="Search"][aria-label="search"]')
        self.clear_button: Locator = page.locator('button#input-clear')
        self.no_users_text: Locator = page.locator('p.MuiTypography-root:has-text("There are no users yet")')
        self.empty_image: Locator = page.locator('img[alt="Lonely niffler"]')

    def get_tab(self, tab_name: str) -> Locator:
        return self.tabs.filter(has_text=tab_name)

    def select_tab(self, tab_name: str):
        self.get_tab(tab_name).click()

    def is_all_people_tab_selected(self) -> bool:
        return self.is_selected(self.tab_all_people)

    def is_friends_tab_selected(self) -> bool:
        return self.is_selected(self.tab_friends)

    def search(self, query: str):
        self.search_input.fill(query)
        self.search_input.press("Enter")

    def is_no_users_text_visible(self) -> bool:
        return self.no_users_text.is_visible()

    def is_empty_image_visible(self) -> bool:
        return self.empty_image.is_visible()

    def get_no_users_text(self) -> str:
        return self.no_users_text.inner_text()

    @staticmethod
    def is_selected(locator: Locator) -> bool:
        return locator.get_attribute("aria-selected") == "true"
