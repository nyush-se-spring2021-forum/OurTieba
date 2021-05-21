class TestSubscribe:
    """
    Test func "subscribe" in api.py. If a user has already subscribed/unsubscribed but sends an request with action =
    "1"/"0", this request is perfectly fine and not considered fault. In this case, only LMT will be updated.
    """
    def test_1(self, subscribe):  # not logged in
        res = subscribe.subscribe(Bid=2, action="1")
        assert b"Please sign in" in res.content

    def test_2(self, auth, subscribe):  # subscribe: correct (because U1 hasn't subscribed B2, and B2 has 0 subs count)
        auth.login()
        res = subscribe.subscribe(Bid=2, action="1")
        assert res.json()["subs_count"] == 1
        assert res.json()["status"] == 1
        auth.logout()

    def test_3(self, auth, subscribe):  # unsubscribe: correct (because U1 just subscribed B2, and B2 has 1 subs count)
        auth.login()
        res = subscribe.subscribe(Bid=2, action="0")
        assert res.json()["subs_count"] == 0
        assert res.json()["status"] == 1
        auth.logout()

    def test_4(self, auth, subscribe):  # wrong action
        auth.login()
        res = subscribe.subscribe(Bid=2, action="hh")
        assert b"Invalid data." in res.content
        auth.logout()

    def test_5(self, auth, subscribe):  # invalid Bid (note that all IDs are strictly positive)
        auth.login()
        res = subscribe.subscribe(Bid=0, action="1")
        assert b"Board not found." in res.content
        auth.logout()

    def test_6(self, auth, subscribe):  # subscribe: correct (reason in docstring of this class)
        auth.login()
        res = subscribe.subscribe(Bid=1, action="1")
        assert res.json()["subs_count"] == 1
        assert res.json()["status"] == 1
        auth.logout()
