import time

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@allure.feature("商品搜索")
@pytest.mark.ui
class TestProducts:
    def test_search(self, driver, web_url):
        driver.get(f"{web_url}/products")
        time.sleep(1)
        search = driver.find_element(By.XPATH, "//input[@placeholder='搜索商品、品牌、店铺、标签、使用场景']")
        time.sleep(1)
        search.send_keys("耳机")
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(.,'搜索')]").click()
        time.sleep(1)
        WebDriverWait(driver, 30).until(lambda d: "AI 降噪蓝牙耳机" in d.page_source)
        # 断言：命中目标商品，且不包含其它分类商品
        assert "AI 降噪蓝牙耳机" in driver.page_source
        assert "MateBook" not in driver.page_source

    def test_category_filter(self, driver, web_url, click):
        driver.get(f"{web_url}/products")
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[contains(@class,'el-select')]").click()
        time.sleep(1)
        option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(@class,'el-select-dropdown__item')][.//span[contains(.,'手机数码')]]")
            )
        )
        click(option)
        time.sleep(1)
        WebDriverWait(driver, 30).until(lambda d: "AI 降噪蓝牙耳机" in d.page_source)
        # 断言：仅剩手机数码分类商品
        assert "AI 降噪蓝牙耳机" in driver.page_source
        assert "5G 全网通智能手机" in driver.page_source
        assert "MateBook" not in driver.page_source
