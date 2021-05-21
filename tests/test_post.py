class TestPost:
    """
    Test all functions relating to post in api.py.
    """

    def test_1(self, post):  # not logged in
        res = post.add(Bid=1, title="Hello", content="<p>Hello</p>", text="Hello")
        assert b"Please sign in" in res.content

    def test_2(self, auth, post):  # add: correct
        auth.login()  # default user is U1
        res = post.add(Bid=1, title="Hello", content="<p>Hello</p>", text="Hello")
        assert res.json()["status"] == 1
        auth.logout()

    def test_3(self, auth, post):  # delete: correct (because post1 is owned by U1)
        auth.login()
        res = post.delete(Pid=1)
        assert res.json()["status"] == 1
        auth.logout()

    def test_4(self, auth, post):  # restore: correct (because post1 is just deleted by U1)
        auth.login()
        res = post.restore(Pid=1)
        assert res.json()["status"] == 1
        auth.logout()

    def test_5(self, auth, post):  # like: correct (because now U1 does not like post1)
        auth.login()
        res = post.like(Pid=1)
        assert res.json()["cur_status"] == 1
        assert res.json()["status"] == 1
        auth.logout()

    def test_6(self, auth, post):  # unlike: correct (because U1 just liked post1)
        auth.login()
        res = post.like(Pid=1)
        assert res.json()["cur_status"] == 0
        assert res.json()["status"] == 1
        auth.logout()

    def test_7(self, auth, post):  # undislike: correct (because now U6 dislikes post1)
        auth.login(uname="U6", password="666")  # logged in as U6
        res = post.dislike(Pid=1)
        assert res.json()["cur_status"] == 0
        assert res.json()["status"] == 1
        auth.logout()

    def test_8(self, auth, post):  # dislike: correct (because U6 just undisliked post1)
        auth.login(uname="U6", password="666")  # logged in as U6
        res = post.dislike(Pid=1)
        assert res.json()["cur_status"] == 1
        assert res.json()["status"] == 1
        auth.logout()

    def test_9(self, auth, client, post):  # like/dislike: wrong target, empty target_id
        auth.login()
        res = client.post("/api/like", data={"target": "whatever", "Pid": 3})
        assert b"Invalid data." in res.content

        res = post.like(Pid=None)
        assert b"Invalid data." in res.content

        res = client.post("/api/dislike", data={"target": "whatever", "Pid": 4})
        assert b"Invalid data." in res.content

        res = post.dislike(Pid=None)
        assert b"Invalid data." in res.content
        auth.logout()

    def test_10(self, auth, post):  # like/dislike: invalid target ID
        auth.login()
        res = post.like(Pid=0)
        assert b"Target not found." in res.content

        res = post.dislike(Pid=0)
        assert b"Target not found." in res.content
        auth.logout()
