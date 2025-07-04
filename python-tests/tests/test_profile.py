from time import sleep

from pages.main_page import MainPage
from pages.profile_page import ProfilePage


def test_goto_profile(page_factory, login):
    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
    main_page.open_profile()
    profile_page: ProfilePage = page_factory(ProfilePage)
    assert profile_page.is_title_visible()


def test_add_new_category(page_factory, login):
    category: str = "Красота"
    profile_page: ProfilePage = page_factory(ProfilePage)
    profile_page.goto()
    profile_page.add_category(category)
    assert category in profile_page.get_categories()
