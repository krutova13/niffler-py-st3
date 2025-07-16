from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.components.archive_dialog import ArchiveCategoryDialog


class ProfilePage(BasePage):
    URL: str = "/profile"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page = page
        self.archive_dialog = ArchiveCategoryDialog(page)
        self.title: Locator = page.locator('h2:has-text("Profile")')
        self.avatar: Locator = page.locator('div.MuiAvatar-root')
        self.upload_btn: Locator = page.locator('label[for="image__input"] span:has-text("Upload new picture")')
        self.upload_input: Locator = page.locator('input#image__input')
        self.username: Locator = page.locator('input#username')
        self.name_input: Locator = page.locator('input#name')
        self.save_btn: Locator = page.locator('button[type="submit"]:has-text("Save changes")')
        self.categories_title: Locator = page.locator('h2:has-text("Categories")')
        self.show_archived_switch: Locator = page.locator('span.MuiSwitch-root input[type="checkbox"]')
        self.add_category_input: Locator = page.locator('input[placeholder="Add new category"]')
        self.edit_category_input: Locator = page.locator('input[placeholder="Edit category"]')
        self.category_chips: Locator = page.locator('div.MuiChip-root')
        self.archive_category_btns: str = 'button[aria-label="Archive category"]'
        self.unarchive_category_btns: str = 'button[aria-label="Unarchive category"]'
        self.category_box: str = 'div.MuiBox-root:has(span.MuiChip-label:has-text("{category_name}"))'
        self.edit_category_btns: str = 'button[aria-label="Edit category"]'
        self.error_text = page.locator('span.input__helper-text')

    def goto(self):
        self.page.goto(f"{self.base_url}{self.URL}")

    def is_title_visible(self) -> bool:
        self.title.wait_for(timeout=3000)
        return self.title.is_visible()

    def upload_new_picture(self, file_path: str):
        self.upload_input.set_input_files(file_path)

    def get_username(self) -> str:
        return self.username.input_value()

    def set_name(self, name: str):
        self.name_input.fill(name)

    def save_changes(self):
        self.save_btn.click()

    def add_category(self, category: str):
        self.add_category_input.fill(category)
        self.add_category_input.press("Enter")
        self.category_chips.filter(has_text=category).first.wait_for(state="visible", timeout=3000)

    def set_new_category(self, category: str):
        self.edit_category_input.fill(category)
        self.edit_category_input.press("Enter")

    def set_new_category_and_wait_for_visible(self, category: str):
        self.set_new_category(category)
        self.category_chips.filter(has_text=category).first.wait_for(state="visible", timeout=3000)

    def get_categories(self) -> list[str]:
        return self.category_chips.all_inner_texts()

    def is_switch_on(self) -> bool:
        return self.show_archived_switch.is_checked()

    def toggle_show_archived(self):
        self.show_archived_switch.click()

    def get_category_box(self, category_name: str) -> Locator:
        locator_str = self.category_box.format(category_name=category_name)
        return self.page.locator(locator_str)

    def click_btn_edit_category(self, category_name: str):
        self.get_category_box(category_name).locator(self.edit_category_btns).click()

    def click_btn_archive_category(self, category_name: str):
        self.get_category_box(category_name).locator(self.archive_category_btns).click()

    def click_btn_unarchive_category(self, category_name: str):
        self.get_category_box(category_name).locator(self.unarchive_category_btns).click()

    def edit_category(self, category_name: str, new_value: str):
        self.click_btn_edit_category(category_name)
        self.set_new_category_and_wait_for_visible(new_value)

    def archive_category(self, category_name: str):
        self.click_btn_archive_category(category_name)
        self.archive_dialog.click_archive()
        self.page.wait_for_selector(
            self.category_box.format(category_name=category_name),
            state="detached",
            timeout=5000
        )

    def unarchive_category(self, category_name: str):
        self.click_btn_unarchive_category(category_name)
        self.archive_dialog.click_unarchive()
        self.title.wait_for(state="visible", timeout=3000)

    def get_error_text_allowed_length(self) -> str:
        return self.error_text.inner_text()
