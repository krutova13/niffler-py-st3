from playwright.sync_api import Locator

from pages.base_page import BasePage


class ProfilePage(BasePage):
    URL: str = "/profile"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.title: Locator = page.locator('h2:has-text("Profile")')
        self.avatar: Locator = page.locator('div.MuiAvatar-root')
        self.upload_btn: Locator = page.locator('label[for="image__input"] span:has-text("Upload new picture")')
        self.upload_input: Locator = page.locator('input#image__input')
        self.username_input: Locator = page.locator('input#username')
        self.name_input: Locator = page.locator('input#name')
        self.save_btn: Locator = page.locator('button[type="submit"]:has-text("Save changes")')
        self.categories_title: Locator = page.locator('h2:has-text("Categories")')
        self.show_archived_switch: Locator = page.locator('span.MuiSwitch-root input[type="checkbox"]')
        self.add_category_input: Locator = page.locator('input#category')
        self.category_chips: Locator = page.locator('div.MuiChip-root')
        self.edit_category_btns: Locator = page.locator('button[aria-label="Edit category"]')
        self.archive_category_btns: Locator = page.locator('button[aria-label="Archive category"]')

    def goto(self):
        self.page.goto(f"{self.base_url}{self.URL}")

    def is_title_visible(self) -> bool:
        self.title.wait_for(timeout=3000)
        return self.title.is_visible()

    def upload_new_picture(self, file_path: str):
        self.upload_input.set_input_files(file_path)

    def set_name(self, name: str):
        self.name_input.fill(name)

    def save_changes(self):
        self.save_btn.click()

    def add_category(self, category: str):
        self.add_category_input.fill(category)
        self.add_category_input.press("Enter")
        self.category_chips.filter(has_text=category).first.wait_for(state="visible", timeout=3000)

    def get_categories(self) -> list[str]:
        return self.category_chips.all_inner_texts()

    def edit_first_category(self):
        self.edit_category_btns.first.click()

    def archive_first_category(self):
        self.archive_category_btns.first.click()

    def toggle_show_archived(self):
        self.show_archived_switch.check() if not self.show_archived_switch.is_checked() else self.show_archived_switch.uncheck()
