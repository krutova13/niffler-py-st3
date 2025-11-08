from playwright.sync_api import Page, Locator


class ArchiveCategoryDialog:
    def __init__(self, page: Page):
        self.page = page
        self.dialog: Locator = page.locator('div[role="dialog"][aria-describedby="alert-dialog-slide-description"]')
        self.title: Locator = self.dialog.locator('h2')
        self.description: Locator = self.dialog.locator('[aria-describedby="alert-dialog-slide-description"]')
        self.close_button: Locator = self.dialog.locator('button:has-text("Close")')
        self.archive_button: Locator = self.dialog.locator('button:has-text("Archive")')
        self.unarchive_button: Locator = self.dialog.locator('button:has-text("Unarchive")')

    def is_visible(self) -> bool:
        return self.dialog.is_visible()

    def get_title(self) -> str:
        return self.title.inner_text()

    def get_description(self) -> str:
        return self.description.inner_text()

    def click_close(self):
        self.close_button.click()

    def click_archive(self):
        self.archive_button.click()

    def click_unarchive(self):
        self.unarchive_button.click()
