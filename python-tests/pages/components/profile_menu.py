from playwright.sync_api import Page, Locator


class ProfileMenu:
    def __init__(self, page: Page):
        self.page = page
        self.menu: Locator = page.locator('div.MuiPopover-paper[role="presentation"] ul[role="menu"]')
        self.profile_link: Locator = page.locator('a[href="/profile"]')
        self.friends_link: Locator = page.locator('a[href="/people/friends"]')
        self.all_people_link: Locator = page.locator('a[href="/people/all"]')
        self.sign_out_btn: Locator = page.locator('li:has-text("Sign out")')

    def is_visible(self) -> bool:
        return self.menu.is_visible()

    def go_to_profile(self):
        self.profile_link.click()

    def go_to_friends(self):
        self.friends_link.click()

    def go_to_all_people(self):
        self.all_people_link.click()

    def sign_out(self):
        self.sign_out_btn.click()
