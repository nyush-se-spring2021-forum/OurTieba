class TestAuth:
    """
    Test all functions relating to authentication in api.py. Logout is designed always to return success (even if user
    not logged in), since its job is to clear session data.
    """

    def test_1(self, auth):  # login and logout: correct input and method
        res = auth.login(uname="U1", password="111")
        assert res.headers.get("Set-Cookie") is not None
        assert res.json()["status"] == 1
        # logout to clear session
        res = auth.logout()
        assert "session=; Expires=Thu, 01-Jan-1970 00:00:00 GMT; Max-Age=0;" in res.headers.get("Set-Cookie")
        assert res.json()["status"] == 1

    def test_2(self, client):  # login: wrong method
        res = client.get("/api/auth/login", data={"uname": "U1", "password": "111"})
        assert res.status_code == 404

    def test_3(self, auth):  # login: non-existent username
        res = auth.login(uname="0.30000000000000004", password="111")
        assert b"Username does not exist." in res.content

    def test_4(self, auth):  # login: wrong password
        res = auth.login(uname="U1", password="000")
        assert b"Incorrect password." in res.content

    def test_5(self, auth):  # login: empty input
        res = auth.login(uname=None, password=None)
        assert b"Invalid input." in res.content

    def test_6(self, auth):  # register: correct
        res = auth.register(uname="foobar", password="@123456a", nickname="Hook")
        assert res.json()["status"] == 1
        auth.logout()  # clear session

        res = auth.login(uname="foobar", password="@123456a")
        assert res.headers.get("Set-Cookie") is not None
        assert res.json()["status"] == 1
        auth.logout()

    def test_7(self, auth):  # register: invalid uname/password/nickname
        res = auth.register(uname="foo", password="@123456a", nickname="Hook")
        assert b"Username must be of length 5 ~ 20." in res.content

        res = auth.register(uname="foo123", password="12345678", nickname="Hook")
        assert b"Invalid password." in res.content

        res = auth.register(uname="foo123", password="@123456a", nickname="H" * 21)
        assert b"Invalid nickname." in res.content
