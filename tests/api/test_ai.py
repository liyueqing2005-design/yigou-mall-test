import allure
import pytest


@allure.feature("AI 导购")
@pytest.mark.api
class TestAi:
    def test_chat_shopping(self, http, ok):
        body = ok(http.post("/ai/chat", json={
            "userId": 1, "question": "推荐学生数码好物", "scene": "shopping",
        }, timeout=90))
        answer = body["data"]
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_chat_after_sale(self, http, ok):
        body = ok(http.post("/ai/chat", json={
            "userId": 1, "question": "退货需要什么", "scene": "afterSale",
        }, timeout=90))
        assert isinstance(body["data"], str)
        assert len(body["data"]) > 0

    def test_history(self, http, ok):
        body = ok(http.get("/ai/history", params={"userId": 1, "scene": "shopping"}))
        assert isinstance(body["data"], list)

    def test_delete_history(self, http, ok):
        body = ok(http.delete("/ai/history", json={"userId": 1, "ids": ["nonexistent"]}))
        assert body["data"] is True

    def test_stream(self, http):
        resp = http.get("/ai/stream", params={"userId": 1, "question": "推荐耳机"},
                        stream=True, timeout=90)
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("Content-Type", "")
        chunks = [line for line in resp.iter_lines(decode_unicode=True) if line]
        assert chunks
