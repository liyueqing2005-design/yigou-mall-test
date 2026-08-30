"""易购商城自动化测试（Python + pytest + requests + Selenium）。

运行方式（在项目根目录执行）：

    接口测试      pytest tests/api -m api
    界面测试      pytest tests/ui -m ui
    全部测试      pytest tests

可选参数：

    --api-url   接口基础地址，默认 http://localhost:8080/api
    --web-url   前端地址，默认 http://localhost:5173
    --headed    有界面模式运行浏览器（默认无头）

前置条件：

    1. MySQL 已按 sql/init.sql 初始化，后端启动于 8080
    2. 前端启动于 5173（仅 UI 测试需要）
    3. UI 测试需本机安装 Chrome
"""

import pytest
import requests

from tests.config import API_URL, WEB_URL, BUYER


def pytest_configure(config):
    config.addinivalue_line("markers", "api: 接口自动化测试（requests）")
    config.addinivalue_line("markers", "ui: 界面自动化测试（Selenium）")


def pytest_addoption(parser):
    parser.addoption("--api-url", default=API_URL, help="接口基础地址")
    parser.addoption("--web-url", default=WEB_URL, help="前端地址")
    parser.addoption("--headless", action="store_true", default=False, help="无界面模式（后台运行，不弹浏览器）")
    parser.addoption("--slow", action="store_true", default=False, help="放慢操作节奏，便于观察页面变化")


@pytest.fixture(scope="session")
def api_url(request):
    return request.config.getoption("--api-url").rstrip("/")


@pytest.fixture(scope="session")
def web_url(request):
    return request.config.getoption("--web-url").rstrip("/")


class ApiClient:
    def __init__(self, base):
        self.base = base

    def request(self, method, path, **kwargs):
        return requests.request(method, self.base + path, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


@pytest.fixture(scope="session")
def http(api_url):
    return ApiClient(api_url)


@pytest.fixture(scope="session")
def ok():
    def _ok(resp, code=200):
        assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text[:200]}"
        body = resp.json()
        assert body.get("code") == code, f"期望 code={code}，实际 {body}"
        return body

    return _ok


@pytest.fixture(scope="session")
def new_order(http, ok):
    def _create(user_id=BUYER["id"]):
        http.delete("/cart", params={"userId": user_id})
        http.post("/cart", json={"userId": user_id, "productId": 5, "quantity": 1})
        body = ok(http.post("/orders/checkout", json={
            "userId": user_id,
            "receiverName": "测试买家",
            "phone": "13800138000",
            "address": "广州市天河区测试地址",
        }))
        return body["data"]

    return _create
