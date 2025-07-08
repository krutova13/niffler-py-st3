from pages.main_page import MainPage
from pages.spending.add_spending_page import AddSpendingPage
from pages.spending.edit_spending_page import EditSpendingPage


def test_create_new_spending(page_factory, login):
    amount: str = "500"
    category: str = "Транспорт"
    date: list = ["03/06/2025", "Mar 06, 2025"]
    description: str = "Тест"

    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
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


def test_edit_spending_amount(page_factory, login, created_spend):
    amount: str = "2000"
    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
    main_page.edit_spending()
    edit_spending: EditSpendingPage = page_factory(EditSpendingPage)
    edit_spending.fill_amount(amount)
    edit_spending.save()
    assert main_page.is_last_spending_amount(expected=amount)


def test_edit_spending_currency(page_factory, login, created_spend):
    currency: str = "$"
    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
    main_page.edit_spending()
    edit_spending: EditSpendingPage = page_factory(EditSpendingPage)
    edit_spending.select_currency(currency)
    edit_spending.save()
    assert main_page.is_last_spending_amount(expected=created_spend.amount, currency=currency)


def test_edit_spending_category(page_factory, login, created_spend):
    category: str = "Развлечения"
    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
    main_page.edit_spending()
    edit_spending: EditSpendingPage = page_factory(EditSpendingPage)
    edit_spending.fill_category(category)
    edit_spending.save()
    assert main_page.is_last_spending_category(category)


def test_search_spending(page_factory, login, created_spend):
    not_valid_search: str = "999qwe"
    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
    main_page.search(created_spend.category.name)
    assert main_page.is_last_spending_category(created_spend.category.name)
    main_page.clear_search()
    main_page.search(not_valid_search)
    assert main_page.is_no_spendings_placeholder_visible()


def test_delete_all_spendings(page_factory, login, created_spend):
    main_page: MainPage = page_factory(MainPage)
    main_page.goto()
    main_page.select_all_spendings()
    main_page.delete_selected()
    main_page.confirm_delete()
    assert main_page.is_no_spendings_placeholder_visible()
