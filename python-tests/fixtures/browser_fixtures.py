import os
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=os.getenv("HEADLESS", "false").lower() == "true",
            slow_mo=int(os.getenv("SLOW_MO", "0"))
        )
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser, request: pytest.FixtureRequest) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    yield context

    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        test_name = request.node.name.replace("/", "_")
        if context.pages:
            page = context.pages[0]
            screenshot_path = f"artifacts/{test_name}.png"
            page.screenshot(path=screenshot_path, full_page=True)

            # Прикрепить скриншот к Allure отчету
            import allure
            from allure_commons.types import AttachmentType
            with open(screenshot_path, 'rb') as f:
                allure.attach(
                    f.read(),
                    name=f"Скриншот ошибки: {test_name}",
                    attachment_type=AttachmentType.PNG
                )

            try:
                html_content = page.content()
                allure.attach(
                    html_content,
                    name=f"HTML страницы: {test_name}",
                    attachment_type=AttachmentType.HTML
                )
            except Exception:
                pass

    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page
    page.close()
