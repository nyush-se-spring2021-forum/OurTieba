class TestUpload:
    """
    Test func "handle_upload" in api.py. Will not test large image or video because it takes time to upload to Github.
    """

    def test_1(self, upload):  # wrong method for config
        res = upload.upload_file(action="config", files=None)
        assert b"Something went wrong." in res.content

    def test_2(self, upload):  # action = "config": correct
        res = upload.config()
        assert b"imageActionName" in res.content

    def test_3(self, auth, upload):  # action = "uploadavatar": correct
        auth.login()
        res = upload.upload_file(action="uploadavatar", files={"file": ("test", open("tests/test.jpg", "rb"),
                                                                        "image/jpeg")})
        assert res.json()["status"] == 1
        auth.logout()

    def test_4(self, auth, upload):  # action = "uploadimage": correct
        auth.login()
        res = upload.upload_file(action="uploadimage", files={"upfile": ("test", open("tests/test.jpg", "rb"),
                                                                         "image/jpeg")})
        assert res.json()["state"] == "SUCCESS"
        auth.logout()

    def test_5(self, auth, upload):  # action = "uploadvideo": correct
        auth.login()
        res = upload.upload_file(action="uploadvideo", files={"upfile": ("test", open("tests/test.mp4", "rb"),
                                                                         "video/mp4")})
        assert res.json()["state"] == "SUCCESS"
        auth.logout()

    def test_6(self, auth, upload):  # wrong action
        auth.login()
        res = upload.upload_file(action="whatever", files={"upfile": ("test", open("tests/test.jpg", "rb"),
                                                                      "image/jpeg")})
        assert b"Something went wrong." in res.content
        auth.logout()

    def test_7(self, auth, upload):  # no file
        auth.login()
        res = upload.upload_file(action="uploadimage", files=None)
        assert b"Please upload a file." in res.content
        auth.logout()

    def test_8(self, auth, upload):  # wrong file format
        auth.login()
        res = upload.upload_file(action="uploadimage", files={"upfile": ("test", open("tests/test.mp4", "rb"),
                                                                         "video/mp4")})
        assert b"Invalid file type." in res.content
        auth.logout()
