import allure

from marks import Pages, TestData
from utils.allure_helpers import Epic, Feature, Story

TEST_CATEGORY = "Такси"


@allure.epic(Epic.ui)
@allure.feature(Feature.category)
@allure.story(Story.api_crud)
@allure.title("Получение категории в профиле")
@Pages.main_page
@TestData.category(TEST_CATEGORY)
def test_get_category(main_page, profile_page, test_category):
    main_page.open_profile()
    list_of_categories: list[str] = profile_page.get_categories()
    assert test_category in list_of_categories


@allure.epic(Epic.ui)
@allure.feature(Feature.category)
@allure.story(Story.api_crud)
@allure.title("Получение категории при создании новой траты")
@Pages.main_page
@TestData.category(TEST_CATEGORY)
@TestData.spends("spend_data")
def test_get_category_in_new_spending(main_page, add_spending_page, test_spend, test_category):
    main_page.open_profile()
    main_page.create_new_spending()
    assert add_spending_page.is_chips_visible(test_category)


@allure.epic(Epic.ui)
@allure.feature(Feature.category)
@allure.story(Story.api_crud)
@allure.title("Редактирование категории")
@Pages.main_page
@TestData.category(TEST_CATEGORY)
def test_edit_category(main_page, profile_page, test_category):
    new_category_value: str = "Новое значение"
    main_page.open_profile()
    profile_page.edit_category(test_category, new_category_value)
    list_of_categories: list[str] = profile_page.get_categories()
    assert new_category_value in list_of_categories


@allure.epic(Epic.ui)
@allure.feature(Feature.category)
@allure.story(Story.boundary_tests)
@allure.title("Редактирование категории с невалидным значением")
@Pages.main_page
@TestData.category(TEST_CATEGORY)
def test_edit_category_not_valid_value(main_page, profile_page, test_category):
    empty_category_value: str = ""
    error_text: str = "Allowed category length is from 2 to 50 symbols"
    main_page.open_profile()
    profile_page.click_btn_edit_category(test_category)
    profile_page.set_new_category(empty_category_value)
    assert profile_page.get_error_text_allowed_length() == error_text


@allure.epic(Epic.ui)
@allure.feature(Feature.category)
@allure.story(Story.api_crud)
@allure.title("Архивация и разархивация категории")
@Pages.main_page
@TestData.category(TEST_CATEGORY)
def test_archive_and_unarchive_category(main_page, profile_page, test_category):
    main_page.open_profile()
    profile_page.archive_category(test_category)
    assert test_category not in profile_page.get_categories()
    profile_page.toggle_show_archived()
    assert test_category in profile_page.get_categories()
    profile_page.unarchive_category(test_category)
    profile_page.toggle_show_archived()
    assert test_category in profile_page.get_categories()
