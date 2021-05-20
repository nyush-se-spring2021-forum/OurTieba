import os
import sys

import pytest

sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))

from ourtieba import scrapper


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium


@pytest.fixture(scope="class")
def client():
    my_spider = scrapper.scrapperFactory.produce()
    my_spider.base_url = "http://127.0.0.1:5000"
    return my_spider


class AuthActions:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/auth"

    def login(self, uname='U1', password='111'):
        return self._client.post(self.endpoint + '/login', data={'uname': uname, 'password': password})

    def logout(self):
        return self._client.post(self.endpoint + '/logout')

    def register(self, uname, password, nickname):
        return self._client.post(self.endpoint + "/register", data={"uname": uname, "password": password,
                                                                    "nickname": nickname})


@pytest.fixture
def auth(client):
    return AuthActions(client)


class PostActions:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/post"

    def add(self, Bid, title, content, text):
        return self._client.post(self.endpoint + '/add', data={'Bid': Bid, 'title': title, 'content': content,
                                                               'text': text})

    def delete(self, Pid):
        return self._client.post(self.endpoint + '/delete', data={'Pid': Pid})

    def restore(self, Pid):
        return self._client.post(self.endpoint + '/restore', data={'Pid': Pid})

    def like(self, Pid):
        return self._client.post('/api/like', data={'target': "post", 'id': Pid})

    def dislike(self, Pid):
        return self._client.post('/api/dislike', data={'target': "post", 'id': Pid})


@pytest.fixture
def post(client):
    return PostActions(client)


class CommentActions:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/comment"

    def add(self, Pid, content, text):
        return self._client.post(self.endpoint + '/add', data={'Pid': Pid, 'content': content, 'text': text})

    def delete(self, Cid):
        return self._client.post(self.endpoint + '/delete', data={'Cid': Cid})

    def restore(self, Cid):
        return self._client.post(self.endpoint + '/restore', data={'Cid': Cid})

    def like(self, Cid):
        return self._client.post('/api/like', data={'target': "comment", 'id': Cid})

    def dislike(self, Cid):
        return self._client.post('/api/dislike', data={'target': "comment", 'id': Cid})


@pytest.fixture
def comment(client):
    return CommentActions(client)


class UploadActions:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/upload"

    def config(self):
        return self._client.get(self.endpoint + "?action=config")

    def upload_file(self, action, files):
        return self._client.post(self.endpoint + f"?action={action}", files=files)


@pytest.fixture
def upload(client):
    return UploadActions(client)


class ReportActions:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/report"

    def add(self, target, id, reason):
        return self._client.post(self.endpoint + "/add", data={"target": target, "id": id, "reason": reason})


@pytest.fixture
def report(client):
    return ReportActions(client)


class PersonalInfoActions:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/personal_info"

    def add(self, nickname="", gender="", phone_number="", email="", address="", date_of_birth=""):
        return self._client.post(self.endpoint + "/add",
                                 data={"nickname": nickname, "gender": gender, "phone_number": phone_number,
                                       "email": email, "address": address, "date_of_birth": date_of_birth})


@pytest.fixture
def personal_info(client):
    return PersonalInfoActions(client)


class SubscribeAction:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/subscribe"

    def subscribe(self, Bid, action):
        return self._client.post(self.endpoint, data={"Bid": Bid, "action": action})


@pytest.fixture
def subscribe(client):
    return SubscribeAction(client)


class FetchAction:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/fetch"

    def fetch_data(self, Uid, type_data):
        return self._client.get(self.endpoint + f"?Uid={Uid}&type={type_data}")


@pytest.fixture
def fetch(client):
    return FetchAction(client)


class GetLogAction:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/get_log"

    def get_log(self, t=""):
        return self._client.get(self.endpoint + f"?t={t}")


@pytest.fixture
def get_log(client):
    return GetLogAction(client)


class GetNtfAction:
    def __init__(self, client):
        self._client = client
        self.endpoint = "/api/get_ntf"

    def get_ntf(self, end):
        return self._client.get(self.endpoint + f"?end={end}")


@pytest.fixture
def get_ntf(client):
    return GetNtfAction(client)
