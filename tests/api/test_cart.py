import allure
import pytest

from tests.config import CART_TEST_PRODUCT_ID


def _clear(http):
    http.delete("/cart", params={"userId": 1})


@allure.feature("购物车")
@pytest.mark.api
class TestCart:
    def test_list(self, http, ok):
        body = ok(http.get("/cart", params={"userId": 1}))
        assert isinstance(body["data"], list)

    def test_add_new_item(self, http, ok):
        _clear(http)
        body = ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 2}))
        item = body["data"]
        assert item["productId"] == CART_TEST_PRODUCT_ID
        assert item["quantity"] == 2
        _clear(http)

    def test_add_existing_item_accumulates(self, http, ok):
        _clear(http)
        http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1})
        body = ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1}))
        assert body["data"]["quantity"] == 2
        _clear(http)

    def test_change_quantity(self, http, ok):
        _clear(http)
        item = ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1}))["data"]
        body = ok(http.put(f"/cart/{item['id']}", json={"quantity": 5}))
        assert body["data"]["quantity"] == 5
        _clear(http)

    def test_decrease_quantity(self, http, ok):
        _clear(http)
        item = ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 5}))["data"]
        body = ok(http.put(f"/cart/{item['id']}", json={"quantity": 2}))
        assert body["data"]["quantity"] == 2
        _clear(http)

    def test_change_checked(self, http, ok):
        _clear(http)
        item = ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1}))["data"]
        assert item["checked"] is True
        body = ok(http.put(f"/cart/{item['id']}/checked", json={"checked": False}))
        assert body["data"]["checked"] is False
        _clear(http)

    def test_check_all(self, http, ok):
        _clear(http)
        http.post("/cart", json={"userId": 1, "productId": 5, "quantity": 1})
        http.post("/cart", json={"userId": 1, "productId": 6, "quantity": 1})
        body = ok(http.put("/cart/check-all", json={"userId": 1, "checked": False}))
        assert body["data"] and all(item["checked"] is False for item in body["data"])
        body = ok(http.put("/cart/check-all", json={"userId": 1, "checked": True}))
        assert body["data"] and all(item["checked"] is True for item in body["data"])
        _clear(http)

    def test_add_invalid_product(self, http, ok):
        ok(http.post("/cart", json={"userId": 1, "productId": 999999, "quantity": 1}), code=500)

    def test_change_quantity_invalid_id(self, http, ok):
        ok(http.put("/cart/999999", json={"quantity": 1}), code=500)

    @pytest.mark.xfail(reason="后端未校验数量，quantity<=0 仍被接受，待修复")
    def test_add_quantity_must_be_positive(self, http, ok):
        _clear(http)
        ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 0}), code=500)
        _clear(http)

    def test_remove_item(self, http, ok):
        _clear(http)
        item = ok(http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1}))["data"]
        body = ok(http.delete(f"/cart/{item['id']}"))
        assert body["data"] is True
        listing = ok(http.get("/cart", params={"userId": 1}))
        assert all(i["id"] != item["id"] for i in listing["data"])

    def test_clear_cart(self, http, ok):
        http.post("/cart", json={"userId": 1, "productId": CART_TEST_PRODUCT_ID, "quantity": 1})
        body = ok(http.delete("/cart", params={"userId": 1}))
        assert body["data"] is True
        listing = ok(http.get("/cart", params={"userId": 1}))
        assert listing["data"] == []
