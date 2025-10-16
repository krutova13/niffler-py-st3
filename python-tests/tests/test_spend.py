from marks import TestData, Pages


@Pages.main_page
@TestData.spends("spend_data")
def test_valid_statistics(main_page, test_spend):
    assert main_page.is_statistics_text(
        expected_category=test_spend.category.name,
        expected_amount=test_spend.amount
    )


@Pages.main_page
@TestData.spends("spend_data")
def test_edit_spending_amount(main_page, test_spend, edit_spending_page):
    amount: str = "1000"
    main_page.edit_spending()
    edit_spending_page.fill_amount(amount)
    edit_spending_page.save()
    assert main_page.is_last_spending_amount(expected=amount)


@Pages.main_page
@TestData.spends("spend_data")
def test_edit_spending_currency(main_page, test_spend, edit_spending_page):
    currency: str = "$"
    main_page.edit_spending()
    edit_spending_page.select_currency(currency)
    edit_spending_page.save()
    assert main_page.is_last_spending_amount(expected=test_spend.amount, currency=currency)


@Pages.main_page
@TestData.spends("spend_data")
def test_edit_spending_category(main_page, test_spend, edit_spending_page):
    category: str = "Развлечения"
    main_page.edit_spending()
    edit_spending_page.fill_category(category)
    edit_spending_page.save()
    assert main_page.is_last_spending_category(category)


@Pages.main_page
@TestData.spends("spend_data")
def test_search_spending(main_page, test_spend):
    not_valid_search: str = "999qwe"
    main_page.search(test_spend.category.name)
    assert main_page.is_last_spending_category(test_spend.category.name)
    main_page.clear_search()
    main_page.search(not_valid_search)
    assert main_page.is_no_spendings_placeholder_visible()


@Pages.main_page
def test_create_new_spending(main_page, add_spending_page):
    amount: str = "500"
    category: str = "Транспорт"
    date: list = ["03/06/2020", "Mar 06, 2020"]
    description: str = "Тест"

    main_page.create_new_spending()
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
def test_delete_all_spendings(main_page, test_spend):
    main_page.select_all_spendings()
    main_page.delete_selected()
    main_page.confirm_delete()
    assert main_page.is_no_spendings_placeholder_visible()


@Pages.main_page
def test_get_error_when_add_empty_spending(main_page, add_spending_page):
    main_page.create_new_spending()
    add_spending_page.save()
    assert add_spending_page.get_amount_error_text(), "Amount has to be not less then 0.01"
    assert add_spending_page.get_category_error_text(), "Please choose category"
