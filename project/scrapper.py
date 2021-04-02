from requests_html import HTMLSession, AsyncHTMLSession


class OTSpider:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.session = HTMLSession()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57"}

    def set_cookie(self, cookie):  # if cookie set to None, remove cookie
        self.headers.update({"Cookie": cookie})
        if not cookie:
            self.headers.pop("Cookie")

    def get_hot_news(self, **kwargs):
        url = "https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey=9d51c192354848748d129b08faea32ea"
        res = self.session.get(url, headers=self.headers)
        data = res.json()
        num = kwargs["num"]
        return data["articles"][:num]

    def get_cookie(self, domain="localhost", port=80, uname="U1", password="111"):
        url = f"http://{domain}:{port}/api/auth/login"
        res = self.session.post(url, data={"uname": uname, "password": password}, headers=self.headers)
        cookie = res.headers["Set-Cookie"].split(";")[0]
        return cookie

    def upload_avatar(self, domain="localhost", port=80, uname="U1"):
        url = f"http://{domain}:{port}/api/upload"
        cookie = self.get_cookie(domain=domain, port=port, uname=uname)
        self.set_cookie(cookie)
        file = ("test", open("test.jpg", "rb"), "image/jpeg")  # name, filename, content_type
        res = self.session.post(url, files={"file": file}, headers=self.headers)
        status = res.json().get("status")
        if status:
            print("Upload Successful!")

    def close(self):
        self.session.close()


OT_spider = OTSpider()


class AsyncOTSpider:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.session = AsyncHTMLSession()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57"}

    def set_cookie(self, cookie):
        self.headers.update({"Cookie": cookie})

    def remove_cookie(self):
        if self.headers.get("Cookie"):
            self.headers.pop("Cookie")

    async def get_baidu(self):
        res = await self.session.get("https://www.baidu.com", headers=self.headers)
        return res.html.text

    async def get_bilibili(self):
        res = await self.session.get("https://www.bilibili.com", headers=self.headers)
        return res.html.text

    def run_multitask(self, *args, **kwargs):  # can take in "tasks"(Iterable) as keyword argument
        if kwargs.get("tasks"):
            results = self.session.run(*kwargs["tasks"])
        else:
            results = self.session.run(*args)
        return results


async_spider = AsyncOTSpider()

if __name__ == '__main__':
    # news = spider.get_hot_news(num=3)
    # print(news)
    print(async_spider.run_multitask(async_spider.get_baidu))
    # OT_spider.upload_avatar(port=5000)
