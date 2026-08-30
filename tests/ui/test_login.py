import time

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _fill(driver, xpath, value):
    el = driver.find_element(By.XPATH, xpath)
    driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
        el, value,
    )


def _click(driver, xpath):
    btn = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", btn)


@allure.feature("登录")
@pytest.mark.ui
class TestLogin:
    def test_buyer_login(self, driver, web_url):
        driver.get(f"{web_url}/login")
        time.sleep(1)
        _fill(driver, "(//input)[1]", "buyer")
        time.sleep(1)
        _fill(driver, "//input[@type='password']", "123456")
        time.sleep(1)
        _click(driver, "//button[contains(.,'登录')]")
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(.,'全站热卖')]"))
        )
        # 断言：跳转到首页并展示热卖区
        assert driver.current_url.rstrip("/") == web_url.rstrip("/")
        assert "全站热卖" in driver.page_source

    def test_login_wrong_password(self, driver, web_url):
        driver.get(f"{web_url}/login")
        time.sleep(1)
        _fill(driver, "(//input)[1]", "buyer")
        time.sleep(1)
        _fill(driver, "//input[@type='password']", "wrong")
        time.sleep(1)
        _click(driver, "//button[contains(.,'登录')]")
        time.sleep(1)
        msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'el-message') and contains(.,'账号或密码错误')]"))
        )
        # 断言：出现错误提示，且停留在登录页
        assert "账号或密码错误" in msg.text
        assert driver.current_url.endswith("/login")
