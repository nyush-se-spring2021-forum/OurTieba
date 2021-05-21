class TestComment:
    """
    Test all functions relating to comment in api.py.
    """

    def test_1(self, comment):  # not logged in
        res = comment.add(Pid=1, content="<p>What</p>", text="What")
        assert b"Please sign in" in res.content

    def test_2(self, auth, comment):  # add: correct
        auth.login()  # default user is U1
        res = comment.add(Pid=1, content="<p>What</p>", text="What")
        assert res.json()["status"] == 1
        auth.logout()

    def test_3(self, auth, comment):  # delete: correct (because comment2 is owned by U1)
        auth.login()
        res = comment.delete(Cid=2)
        assert res.json()["status"] == 1
        auth.logout()

    def test_4(self, auth, comment):  # restore: correct (because comment2 is just deleted by U1)
        auth.login()
        res = comment.restore(Cid=2)
        assert res.json()["status"] == 1
        auth.logout()

    def test_5(self, auth, comment):  # like: correct (because now U1 does not like comment2)
        auth.login()
        res = comment.like(Cid=2)
        assert res.json()["cur_status"] == 1
        assert res.json()["status"] == 1
        auth.logout()

    def test_6(self, auth, comment):  # unlike: correct (because U1 just liked comment2)
        auth.login()
        res = comment.like(Cid=2)
        assert res.json()["cur_status"] == 0
        assert res.json()["status"] == 1
        auth.logout()

    def test_7(self, auth, comment):  # undislike: correct (because now U1 dislikes comment1)
        auth.login()
        res = comment.dislike(Cid=1)
        assert res.json()["cur_status"] == 0
        assert res.json()["status"] == 1
        auth.logout()

    def test_8(self, auth, comment):  # dislike: correct (because U1 just undisliked comment1)
        auth.login()
        res = comment.dislike(Cid=1)
        assert res.json()["cur_status"] == 1
        assert res.json()["status"] == 1
        auth.logout()

    def test_9(self, auth, client, comment):  # like/dislike: wrong target, empty target_id
        auth.login()
        res = client.post("/api/like", data={"target": "whatever", "Cid": 5})
        assert b"Invalid data." in res.content

        res = comment.like(Cid=None)
        assert b"Invalid data." in res.content

        res = client.post("/api/dislike", data={"target": "whatever", "Cid": 2})
        assert b"Invalid data." in res.content

        res = comment.dislike(Cid=None)
        assert b"Invalid data." in res.content
        auth.logout()

    def test_10(self, auth, comment):  # like/dislike: invalid target ID
        auth.login()
        res = comment.like(Cid=0)
        assert b"Target not found." in res.content

        res = comment.dislike(Cid=0)
        assert b"Target not found." in res.content
        auth.logout()
