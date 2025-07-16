from playwright.sync_api import Page, Locator


class LogoutDialog:
    def __init__(self, page: Page):
        self.page = page
        self.dialog: Locator = page.locator('div[role="dialog"]')
        self.title: Locator = self.dialog.locator('h2')
        self.description: Locator = self.dialog.locator('[aria-describedby="alert-dialog-slide-description"]')
        self.close_button: Locator = self.dialog.locator('button:has-text("Close")')
        self.logout_button: Locator = self.dialog.locator('button:has-text("Log out")')

    def is_visible(self) -> bool:
        return self.dialog.is_visible()

    def get_title(self) -> str:
        return self.title.inner_text()

    def get_description(self) -> str:
        return self.description.inner_text()

    def click_close(self):
        self.close_button.click()

    def click_logout(self):
        self.logout_button.click()
