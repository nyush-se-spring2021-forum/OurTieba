class TestReport:
    """
    For report, only testing add action is enough.
    """
    def test_1(self, report):  # not logged in
        res = report.add(target="post", id=1, reason="Not good!")
        assert b"Please sign in" in res.content

    def test_2(self, auth, report):  # correct
        auth.login()
        res = report.add(target="post", id=1, reason="Not good!")
        assert res.json()["status"] == 1
        auth.logout()

    def test_3(self, auth, report):  # wrong target, empty id/reason
        auth.login()
        res = report.add(target="board", id=3, reason="Not good!")
        assert b"Invalid data." in res.content
        auth.logout()

        auth.login()
        res = report.add(target="post", id=None, reason="Not good!")
        assert b"Invalid data." in res.content
        auth.logout()

        auth.login()
        res = report.add(target="comment", id=2, reason=None)
        assert b"Invalid data." in res.content
        auth.logout()

    def test_4(self, auth, report):  # invalid target ID (note that all IDs are strictly positive)
        auth.login()
        res = report.add(target="comment", id=0, reason="Not good!")
        assert b"Invalid target ID." in res.content
        auth.logout()
