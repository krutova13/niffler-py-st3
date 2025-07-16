from marks import TestData, Pages
from pages.spending.add_spending_page import AddSpendingPage
from pages.spending.edit_spending_page import EditSpendingPage


@Pages.main_page
@TestData.spends("spend_data")
def test_valid_statistics(page_factory, main_page, spends):
    assert main_page.is_statistics_text(
        expected_category=spends.category.name,
        expected_amount=spends.amount
    )


@Pages.main_page
@TestData.spends("spend_data")
def test_edit_spending_amount(page_factory, main_page, spends):
    amount: str = "1000"
    main_page.edit_spending()
    edit_spending: EditSpendingPage = page_factory(EditSpendingPage)
    edit_spending.fill_amount(amount)
    edit_spending.save()
    assert main_page.is_last_spending_amount(expected=amount)


@Pages.main_page
@TestData.spends("spend_data")
def test_edit_spending_currency(page_factory, main_page, spends):
    currency: str = "$"
    main_page.edit_spending()
    edit_spending: EditSpendingPage = page_factory(EditSpendingPage)
    edit_spending.select_currency(currency)
    edit_spending.save()
    assert main_page.is_last_spending_amount(expected=spends.amount, currency=currency)


@Pages.main_page
@TestData.spends("spend_data")
def test_edit_spending_category(page_factory, main_page, spends):
    category: str = "Развлечения"
    main_page.edit_spending()
    edit_spending: EditSpendingPage = page_factory(EditSpendingPage)
    edit_spending.fill_category(category)
    edit_spending.save()
    assert main_page.is_last_spending_category(category)


@Pages.main_page
@TestData.spends("spend_data")
def test_search_spending(page_factory, main_page, spends):
    not_valid_search: str = "999qwe"
    main_page.search(spends.category.name)
    assert main_page.is_last_spending_category(spends.category.name)
    main_page.clear_search()
    main_page.search(not_valid_search)
    assert main_page.is_no_spendings_placeholder_visible()


@Pages.main_page
def test_create_new_spending(page_factory, main_page):
    amount: str = "500"
    category: str = "Транспорт"
    date: list = ["03/06/2020", "Mar 06, 2020"]
    description: str = "Тест"

    main_page.create_new_spending()
    add_spending_page: AddSpendingPage = page_factory(AddSpendingPage)
    add_spending_page.fill_amount(amount)
    add_spending_page.fill_category(category)
    add_spending_page.fill_date(date[0])
    add_spending_page.fill_description(description)
    add_spending_page.save()
    assert main_page.is_last_spending_amount(expected=amount)
    assert main_page.is_last_spending_category(category)
    assert main_page.is_last_spending_description(description)
    assert main_page.is_last_spending_date(date[1])


@Pages.main_page
@TestData.spends("spend_data")
def test_delete_all_spendings(page_factory, main_page, spends):
    main_page.select_all_spendings()
    main_page.delete_selected()
    main_page.confirm_delete()
    assert main_page.is_no_spendings_placeholder_visible()


@Pages.main_page
def test_get_error_when_add_empty_spending(page_factory, main_page):
    main_page.create_new_spending()
    add_spending_page: AddSpendingPage = page_factory(AddSpendingPage)
    add_spending_page.save()
    assert add_spending_page.get_amount_error_text(), "Amount has to be not less then 0.01"
    assert add_spending_page.get_category_error_text(), "Please choose category"
