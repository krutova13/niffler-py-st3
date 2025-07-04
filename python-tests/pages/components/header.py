from playwright.sync_api import Page, Locator

from pages.components.profile_menu import ProfileMenu


class Header:
    def __init__(self, page: Page):
        self.page = page
        self.menu = ProfileMenu(page)
        self.title: Locator = page.locator('a[href="/main"] h1')
        self.new_spending_btn: Locator = page.locator('a[href="/spending"]')
        self.profile_btn: Locator = page.locator('button[aria-label="Menu"]')

    def click_main_title(self):
        self.title.click()

    def click_new_spending(self):
        self.new_spending_btn.click()

    def open_profile_menu(self):
        self.profile_btn.click()

    def open_profile(self):
        self.profile_btn.click()
        self.menu.go_to_profile()

    def is_title_visible(self) -> bool:
        self.title.wait_for(timeout=3000)
        return self.title.is_visible()
