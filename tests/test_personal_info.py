class TestPersonalInfo:
    """
    Test all functions relating to personal info in api.py. In this phase, only testing add action is enough. Since
    users can choose to update only part of their personal info, tests will focus on each argument separately.
    """

    def test_1(self, personal_info):  # not logged in
        res = personal_info.add(nickname="Hook")
        assert b"Please sign in" in res.content

    def test_2(self, auth, personal_info):  # correct
        auth.login()
        res = personal_info.add(nickname="Hook", email="User1@qq.com", date_of_birth="2000-01-01")
        assert res.json()["status"] == 1
        auth.logout()

    def test_3(self, auth, personal_info):  # nickname too long
        auth.login()
        res = personal_info.add(nickname="H" * 21)
        assert b"Nickname too long." in res.content
        auth.logout()

    def test_4(self, auth, personal_info):  # invalid gender
        auth.login()
        res = personal_info.add(gender="alien")
        assert b"Invalid gender." in res.content
        auth.logout()

    def test_5(self, auth, personal_info):  # invalid phone_number
        auth.login()
        res = personal_info.add(phone_number="12345678abc")
        assert b"Invalid phone number." in res.content
        auth.logout()

    def test_6(self, auth, personal_info):  # invalid email
        auth.login()
        res = personal_info.add(email="User1@qq")
        assert b"Invalid email." in res.content
        auth.logout()

    def test_7(self, auth, personal_info):  # invalid email
        auth.login()
        res = personal_info.add(address="K" * 201)
        assert b"Address too long." in res.content
        auth.logout()

    def test_8(self, auth, personal_info):  # invalid date_of_birth
        auth.login()
        res = personal_info.add(date_of_birth="2000-02-31")
        assert b"Invalid date of birth" in res.content
        auth.logout()
