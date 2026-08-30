import time

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@allure.feature("AI 导购")
@pytest.mark.ui
class TestAi:
    def test_chat(self, driver, web_url):
        driver.get(f"{web_url}/ai")
        time.sleep(1)
        inp = driver.find_element(By.XPATH, "//input[contains(@placeholder,'例如')]")
        time.sleep(1)
        inp.send_keys("推荐学生数码好物")
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(.,'发送')]").click()
        time.sleep(1)
        msg = WebDriverWait(driver, 90).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'chat-message') and contains(@class,'assistant')]")
            )
        )
        # 断言：出现 AI 导购回复，且内容非空
        assert "AI 导购" in msg.text
        answer = msg.find_element(By.XPATH, ".//span").text
        assert answer.strip() != ""
