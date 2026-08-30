import allure
import pytest


@allure.feature("商品")
@pytest.mark.api
class TestProduct:
    def test_list(self, http, ok):
        body = ok(http.get("/products"))
        products = body["data"]
        assert isinstance(products, list)
        assert products
        assert all(p["status"] == "ON_SALE" for p in products)

    def test_search_keyword(self, http, ok):
        body = ok(http.get("/products", params={"keyword": "耳机"}))
        names = [p["name"] for p in body["data"]]
        assert any("耳机" in name for name in names)

    def test_filter_category(self, http, ok):
        body = ok(http.get("/products", params={"category": "手机数码"}))
        assert all(p["category"] == "手机数码" for p in body["data"])

    def test_hot(self, http, ok):
        body = ok(http.get("/products/hot"))
        assert len(body["data"]) <= 12

    def test_detail(self, http, ok):
        body = ok(http.get("/products/2"))
        assert body["data"]["id"] == 2
        assert body["data"]["name"] == "AI 降噪蓝牙耳机"

    def test_detail_not_found(self, http, ok):
        body = ok(http.get("/products/99999"))
        assert body["data"] is None

    def test_crud(self, http, ok):
        created = ok(http.post("/products", json={
            "name": "测试商品", "category": "图书文具", "brand": "TEST",
            "price": 99.0, "stock": 10,
        }))["data"]
        assert created["id"] is not None
        assert created["status"] == "ON_SALE"
        assert created["sellerId"] == 2

        updated = ok(http.put(f"/products/{created['id']}", json={"price": 88.0, "stock": 5}))["data"]
        assert updated["price"] == 88.0

        removed = ok(http.delete(f"/products/{created['id']}"))["data"]
        assert removed is True

        after = ok(http.get(f"/products/{created['id']}"))
        assert after["data"] is None
