class TestClient:
    """
    Test before_request and after_request decorators in __init__.py.
    """

    def test_1(self, client):  # disallowed methods
        res = client.put("/")
        assert res.status_code == 405
        assert b"Method Not Allowed" in res.content

        res = client.options("/api/post/add")
        assert res.status_code == 405
        assert b"Method Not Allowed" in res.content

        res = client.delete("/notifications")
        assert res.status_code == 405
        assert b"Method Not Allowed" in res.content

    def test_2(self, client):  # empty/fake user agent
        res = client.get("/", headers={"User-Agent": ""})
        assert res.status_code == 403
        assert b"No Scrappers!" in res.content

        res = client.get("/board/2", headers={"User-Agent": "python/3.8"})
        assert res.status_code == 403
        assert b"No Scrappers!" in res.content
