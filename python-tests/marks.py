import pytest


class Pages:
    main_page = pytest.mark.usefixtures("main_page")


class TestData:
    category = lambda x: pytest.mark.parametrize("category_name", [x], indirect=True)
    spends = lambda x: pytest.mark.parametrize(
        "spends", [x], indirect=True,
        ids=lambda param: getattr(param, "description", str(param))
    )
