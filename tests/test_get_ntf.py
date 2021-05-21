class TestGetNtf:
    """
    Test func "fetch_ntf" in api.py.
    """

    def test_1(self, get_ntf):  # not logged in
        res = get_ntf.get_ntf(end=0)
        assert b"Please sign in" in res.content

    def test_2(self, auth, get_ntf):  # correct (because U1 has 13 notifications)
        auth.login()
        res = get_ntf.get_ntf(end=0)
        assert res.json()["cursor_end"] == 10
        assert res.json()["is_end"] == 0
        assert res.json()["status"] == 1

        res = get_ntf.get_ntf(end=10)
        assert res.json()["cursor_end"] == 13
        assert res.json()["is_end"] == 1
        assert res.json()["status"] == 1
        auth.logout()

    def test_3(self, auth, get_ntf):  # empty end
        auth.login()
        res = get_ntf.get_ntf(end="")
        assert b"Invalid data." in res.content
        auth.logout()
