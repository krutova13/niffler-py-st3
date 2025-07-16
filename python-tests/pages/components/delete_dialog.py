from playwright.sync_api import Page, Locator


class DeleteDialog:
    def __init__(self, page: Page):
        self.page = page
        self.dialog: Locator = page.locator('div[role="dialog"]')
        self.title: Locator = self.dialog.locator('h2')
        self.description: Locator = self.dialog.locator('p#alert-dialog-slide-description')
        self.cancel_btn: Locator = self.dialog.locator('button:has-text("Cancel")')
        self.delete_btn: Locator = self.dialog.locator('button:has-text("Delete")')

    def confirm(self):
        self.wait_for_visible()
        self.delete_btn.click()

    def cancel(self):
        self.wait_for_visible()
        self.cancel_btn.click()

    def wait_for_visible(self, timeout: int = 3000):
        self.dialog.wait_for(state='visible', timeout=timeout)
