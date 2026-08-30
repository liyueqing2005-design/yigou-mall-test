import allure
import pytest


@allure.feature("知识库")
@pytest.mark.api
class TestKnowledge:
    def test_list(self, http, ok):
        body = ok(http.get("/knowledge"))
        assert isinstance(body["data"], list)
        assert body["data"]

    def test_search(self, http, ok):
        body = ok(http.get("/knowledge", params={"keyword": "退货"}))
        titles = [item["title"] for item in body["data"]]
        assert any("退货" in title for title in titles)

    def test_crud(self, http, ok):
        created = ok(http.post("/knowledge", json={
            "title": "测试知识", "category": "导购", "keywords": "测试", "content": "测试内容",
        }))["data"]
        assert created["enabled"] is True

        updated = ok(http.put(f"/knowledge/{created['id']}", json={"title": "修改后的标题"}))["data"]
        assert updated["title"] == "修改后的标题"

        removed = ok(http.delete(f"/knowledge/{created['id']}"))["data"]
        assert removed is True
