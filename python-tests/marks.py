import pytest


class Pages:
    main_page = pytest.mark.usefixtures("main_page")


class TestData:
    category = lambda x: pytest.mark.parametrize("category_data", [x], indirect=True)
    spends = lambda x: pytest.mark.parametrize(
        "test_spend", [x], indirect=True,
        ids=lambda param: getattr(param, "description", str(param))
    )
    page_info = lambda x: pytest.mark.parametrize(
        "page_info", x,
        ids=lambda param: f"page={param.page}_size={param.size}"
    )
