from marks import Pages


@Pages.main_page
def test_goto_profile(main_page, profile_page):
    main_page.open_profile()
    assert profile_page.is_title_visible()


@Pages.main_page
def test_get_username(main_page, profile_page, user_credentials):
    main_page.open_profile()
    assert profile_page.get_username() == user_credentials.username


@Pages.main_page
def test_goto_friends(main_page, people_page):
    main_page.open_friends()
    assert people_page.is_friends_tab_selected()
    assert not people_page.is_all_people_tab_selected()


@Pages.main_page
def test_goto_all_people(main_page, people_page):
    main_page.open_all_people()
    assert people_page.is_all_people_tab_selected()
    assert not people_page.is_friends_tab_selected()
