import allure
import pytest


@allure.feature("订单")
@pytest.mark.api
class TestOrder:
    def test_list(self, http, ok):
        body = ok(http.get("/orders", params={"userId": 1}))
        orders = body["data"]
        assert isinstance(orders, list)
        if orders:
            assert "productSummary" in orders[0]

    def test_detail(self, http, ok):
        body = ok(http.get("/orders/1"))
        data = body["data"]
        assert data["order"]["id"] == 1
        assert isinstance(data["items"], list)

    def test_checkout(self, http, ok):
        http.delete("/cart", params={"userId": 1})
        http.post("/cart", json={"userId": 1, "productId": 5, "quantity": 1})
        body = ok(http.post("/orders/checkout", json={
            "userId": 1,
            "receiverName": "张三",
            "phone": "13800138000",
            "address": "广州市天河区",
        }))
        order = body["data"]
        assert order["status"] == "PAID"
        assert order["orderNo"].startswith("YG")

    def test_seller_orders(self, http, ok):
        body = ok(http.get("/orders/seller", params={"sellerId": 2}))
        for row in body["data"]:
            assert "productName" in row
            assert "amount" in row

    def test_change_status(self, http, ok):
        body = ok(http.put("/orders/2/status", json={"status": "SHIPPED"}))
        assert body["data"]["status"] == "SHIPPED"
        ok(http.put("/orders/2/status", json={"status": "PAID"}))

    @pytest.mark.xfail(reason="空购物车下单应被拒绝，当前会生成金额为 0 的空订单，待修复")
    def test_checkout_empty_cart(self, http, ok):
        http.delete("/cart", params={"userId": 1})
        ok(http.post("/orders/checkout", json={"userId": 1}), code=500)

    @pytest.mark.xfail(reason="缺少防重复提交/幂等保护，连续两次下单会生成两条订单，待修复")
    def test_double_checkout_single_order(self, http, ok):
        http.delete("/cart", params={"userId": 1})
        http.post("/cart", json={"userId": 1, "productId": 5, "quantity": 1})
        before = ok(http.get("/orders/analysis"))["data"]["orderCount"]
        ok(http.post("/orders/checkout", json={"userId": 1}))
        ok(http.post("/orders/checkout", json={"userId": 1}))
        after = ok(http.get("/orders/analysis"))["data"]["orderCount"]
        assert after - before == 1

    def test_analysis(self, http, ok):
        body = ok(http.get("/orders/analysis"))
        data = body["data"]
        for key in ("orderCount", "gmv", "avgOrderAmount"):
            assert key in data
