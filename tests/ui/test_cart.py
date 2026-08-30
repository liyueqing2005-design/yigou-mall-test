import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.config import CART_TEST_PRODUCT_ID

INCREASE = "//*[contains(@class,'el-input-number__increase')]"
DECREASE = "//*[contains(@class,'el-input-number__decrease')]"
ALL_BOX = "//label[contains(@class,'el-checkbox')][.//span[contains(.,'全选')]]"
DELETE_BTN = "//button[contains(.,'删除')]"
QTY_INPUT = "//div[contains(@class,'el-input-number')]//input"
TOTAL = "//strong[contains(@class,'price')]"


def _qty_ui(driver):
    return driver.find_element(By.XPATH, QTY_INPUT).get_attribute("value")


def _total_ui(driver):
    return driver.find_element(By.XPATH, TOTAL).text


def _checked(driver, xpath):
    return "is-checked" in driver.find_element(By.XPATH, xpath).get_attribute("class")


@allure.feature("购物车")
@pytest.mark.ui
class TestCart:
    def _prepare(self, http):
        http.delete("/cart", params={"userId": 1})
        http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1})

    def _wait_cart(self, driver):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, DELETE_BTN))
        )

    def test_cart_page(self, driver, web_url):
        driver.get(f"{web_url}/cart")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(.,'买家购物车')]"))
        )
        WebDriverWait(driver, 10).until(
            lambda d: ("AI 降噪蓝牙耳机" in d.page_source) or ("购物车是空的" in d.page_source)
        )

    def test_add_decrease_select_all_delete(self, driver, web_url, http, click):
        self._prepare(http)
        driver.get(f"{web_url}/cart")
        self._wait_cart(driver)

        # 初始状态断言
        assert _qty_ui(driver) == "1"
        assert "159.00" in _total_ui(driver)
        assert _checked(driver, ALL_BOX)

        # 1. 加购：数量 +1
        click(driver.find_element(By.XPATH, INCREASE))
        WebDriverWait(driver, 10).until(lambda d: _qty_ui(d) == "2")
        assert _qty_ui(driver) == "2"
        assert "318.00" in _total_ui(driver)

        # 2. 减购：数量 -1
        click(driver.find_element(By.XPATH, DECREASE))
        WebDriverWait(driver, 10).until(lambda d: _qty_ui(d) == "1")
        assert _qty_ui(driver) == "1"
        assert "159.00" in _total_ui(driver)

        # 3. 全选 -> 取消全选 -> 全选
        click(driver.find_element(By.XPATH, ALL_BOX))
        WebDriverWait(driver, 10).until(lambda d: not _checked(d, ALL_BOX))
        assert not _checked(driver, ALL_BOX)

        click(driver.find_element(By.XPATH, ALL_BOX))
        WebDriverWait(driver, 10).until(lambda d: _checked(d, ALL_BOX))
        assert _checked(driver, ALL_BOX)

        # 4. 删除商品
        click(driver.find_element(By.XPATH, DELETE_BTN))
        WebDriverWait(driver, 10).until(lambda d: "购物车是空的" in d.page_source)
        assert "购物车是空的" in driver.page_source
