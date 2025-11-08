import logging
import re
from typing import Optional

import allure
import pytest
from allure_commons.reporter import AllureReporter
from pytest import Item, FixtureDef, FixtureRequest
from sqlalchemy import Engine, event

pytest.hookimpl(hookwrapper=True, trylast=True)


def pytest_runtest_call(item: Item):
    yield
    raw_name = item.name
    sanitized = re.sub(r"\[[^\]]*\]", "", raw_name)
    parts_after_prefix = " ".join(sanitized.split("_")[1:]).strip()
    title_text = parts_after_prefix if parts_after_prefix else sanitized.strip()
    allure.dynamic.title(title_text.title())


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield

    logger = allure_logger(request.config)
    if logger is None:
        return

    last_item = getattr(logger, "get_last_item", None)
    if last_item is None:
        return

    item = last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}] " + " ".join(fixturedef.argname.split("_")).title()


def allure_logger(config) -> Optional[AllureReporter]:
    try:
        listener = config.pluginmanager.get_plugin("allure_listener")
        if hasattr(listener, 'allure_logger'):
            return listener.allure_logger
        return None
    except Exception as e:
        pytest.exit(f"Failed to get Allure logger: {e}")


sql_queries = []


@event.listens_for(Engine, "before_cursor_execute")
def log_sql(conn, cursor, statement, parameters, context, executemany):
    sql_queries.append(f"SQL: {statement}\nParams: {parameters}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item):
    yield
    try:
        if hasattr(item, '_sql_queries') and item._sql_queries:
            allure.attach(
                "\n".join(item._sql_queries),
                name="SQL Queries",
                attachment_type=allure.attachment_type.TEXT
            )
    except Exception as e:
        logging.warning(f"Failed to attach SQL queries: {e}")
