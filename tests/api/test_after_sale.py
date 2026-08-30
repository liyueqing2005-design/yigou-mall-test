import time

import allure
import pytest


@pytest.fixture(scope="module")
def order(new_order):
    return new_order(1)


def _create_after_sale(http, ok, order_id):
    time.sleep(1.1)
    return ok(http.post("/after-sales", json={"orderId": order_id, "userId": 1}))["data"]


@allure.feature("售后")
@pytest.mark.api
class TestAfterSale:
    def test_list(self, http, ok):
        body = ok(http.get("/after-sales", params={"userId": 1}))
        assert isinstance(body["data"], list)

    def test_create(self, http, ok, order):
        body = ok(http.post("/after-sales", json={
            "orderId": order["id"], "userId": 1,
            "type": "RETURN_REFUND", "reason": "七天无理由", "description": "测试售后",
        }))
        req = body["data"]
        assert req["status"] == "PENDING"
        assert req["afterSaleNo"].startswith("SH")
        assert req["orderId"] == order["id"]

    def test_create_invalid_order(self, http, ok):
        body = ok(http.post("/after-sales", json={"orderId": 99999, "userId": 1}), code=500)
        assert body["message"] == "订单不存在"

    def test_create_other_user_order(self, http, ok):
        body = ok(http.post("/after-sales", json={"orderId": 1, "userId": 2}), code=500)
        assert body["message"] == "只能申请自己的订单售后"

    def test_process_approve(self, http, ok, order):
        req = _create_after_sale(http, ok, order["id"])
        body = ok(http.put(f"/after-sales/{req['id']}/process", json={"status": "APPROVED", "result": "同意退款"}))
        assert body["data"]["status"] == "APPROVED"

    def test_appeal_after_reject(self, http, ok, order):
        req = _create_after_sale(http, ok, order["id"])
        ok(http.put(f"/after-sales/{req['id']}/process", json={"status": "REJECTED", "result": "拒绝"}))
        body = ok(http.put(f"/after-sales/{req['id']}/appeal", json={"userId": 1}))
        assert body["data"]["status"] == "APPEALED"

    def test_appeal_invalid_status(self, http, ok, order):
        req = _create_after_sale(http, ok, order["id"])
        body = ok(http.put(f"/after-sales/{req['id']}/appeal", json={"userId": 1}), code=500)
        assert "拒绝" in body["message"]

    def test_analysis(self, http, ok):
        body = ok(http.get("/after-sales/analysis"))
        data = body["data"]
        for key in ("afterSaleCount", "pendingCount", "approvedCount", "rejectedCount", "appealedCount", "refundedCount"):
            assert key in data
