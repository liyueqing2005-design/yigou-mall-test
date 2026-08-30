import allure
import pytest

from tests.config import BUYER


@allure.feature("用户认证")
@pytest.mark.api
class TestAuth:
    def test_login_success(self, http, ok):
        body = ok(http.post("/auth/login", json={"username": BUYER["username"], "password": BUYER["password"]}))
        data = body["data"]
        assert data["id"] == BUYER["id"]
        assert data["role"] == "BUYER"
        assert data["token"] == f"demo-token-{BUYER['id']}"

    def test_login_wrong_password(self, http, ok):
        body = ok(http.post("/auth/login", json={"username": BUYER["username"], "password": "wrong"}), code=500)
        assert body["message"] == "账号或密码错误"
        assert body["data"] is None

    def test_login_unknown_user(self, http, ok):
        body = ok(http.post("/auth/login", json={"username": "nobody", "password": "123456"}), code=500)
        assert body["message"] == "账号或密码错误"

    def test_demo_accounts(self, http, ok):
        body = ok(http.get("/auth/demo-accounts"))
        accounts = body["data"]
        roles = {item["role"] for item in accounts}
        assert {"买家", "卖家", "管理员"} == roles
