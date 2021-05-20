class TestGetLog:

    def test_1(self, get_log):  # not logged in (not incorrect)
        res = get_log.get_log()
        assert res.json()["code"] == -1

    def test_2(self, auth, get_log):  # correct
        auth.login()
        res = get_log.get_log()
        assert res.json()["new_count"] == 2
        assert res.json()["code"] == 200
        auth.logout()

    def test_3(self, auth, get_log):  # begin of UNIX timestamp, should have no new ntfs back then
        auth.login()
        res = get_log.get_log(t=0)
        assert res.json()["code"] == 204
        auth.logout()