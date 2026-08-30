import os
import time

import allure
import pytest


@pytest.fixture(scope="session", autouse=True)
def require_web(web_url):
    import requests
    try:
        requests.get(web_url, timeout=5)
    except Exception:
        pytest.skip(f"前端未启动（{web_url}），跳过 UI 测试")


@pytest.fixture
def driver(request):
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options

    headed = not request.config.getoption("--headless")
    slow = request.config.getoption("--slow")

    opts = Options()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")

    try:
        browser = webdriver.Edge(options=opts)
    except Exception as exc:
        pytest.skip(f"无法启动 Edge，跳过 UI 测试：{exc}")

    browser.implicitly_wait(5)

    if slow:
        orig_find = browser.find_element

        def slow_find(*args, **kwargs):
            time.sleep(1.0)
            return orig_find(*args, **kwargs)

        browser.find_element = slow_find

    yield browser
    browser.quit()


@pytest.fixture
def click(driver):
    def _click(el):
        driver.execute_script(
            "var el = arguments[0];"
            "['mousedown','mouseup','click'].forEach(function(t){"
            "el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window,button:0}));"
            "});", el)

    return _click


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            os.makedirs("screenshots", exist_ok=True)
            path = os.path.join("screenshots", f"{item.name}.png")
            try:
                driver.save_screenshot(path)
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass
