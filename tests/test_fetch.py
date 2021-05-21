class TestFetch:
    """
    Test func "fetch_data" in api.py.
    """
    def test_1(self, fetch):  # correct
        res = fetch.fetch_data(Uid=1, type_data=3)
        assert res.json()["count"] == 2
        assert res.json()["status"] == 1

    def test_2(self, fetch):  # empty Uid/type_data, invalid type_data
        res = fetch.fetch_data(Uid="", type_data=2)
        assert b"Invalid data." in res.content

        res = fetch.fetch_data(Uid=1, type_data=None)
        assert b"Invalid data." in res.content

        res = fetch.fetch_data(Uid=1, type_data=10)
        assert b"Invalid data." in res.content

    def test_3(self, fetch):  # invalid Uid
        res = fetch.fetch_data(Uid=0, type_data=1)
        assert b"User not found." in res.content
