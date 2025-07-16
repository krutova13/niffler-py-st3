from marks import Pages
from pages.people_page import PeoplePage
from pages.profile_page import ProfilePage


@Pages.main_page
def test_goto_profile(page_factory, main_page):
    main_page.open_profile()
    profile_page: ProfilePage = page_factory(ProfilePage)
    assert profile_page.is_title_visible()


@Pages.main_page
def test_get_username(page_factory, main_page, test_user: tuple):
    username, _ = test_user
    main_page.open_profile()
    profile_page: ProfilePage = page_factory(ProfilePage)
    assert profile_page.get_username() == username


@Pages.main_page
def test_goto_friends(page_factory, main_page):
    main_page.open_friends()
    people_page: PeoplePage = page_factory(PeoplePage)
    assert people_page.is_friends_tab_selected()
    assert not people_page.is_all_people_tab_selected()


@Pages.main_page
def test_goto_all_people(page_factory, main_page):
    main_page.open_all_people()
    people_page: PeoplePage = page_factory(PeoplePage)
    assert people_page.is_all_people_tab_selected()
    assert not people_page.is_friends_tab_selected()
