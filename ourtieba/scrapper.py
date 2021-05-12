import datetime

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
        self.cache = {"news": dict()}  # note that this is stateless, which means it is cleared on every restart

    def get(self, *arg, **kwargs):
        return self.session.get(*arg, **kwargs)

    def post(self, *arg, **kwargs):
        return self.session.post(*arg, **kwargs)

    def set_cookie(self, cookie):  # if cookie set to None, remove cookie
        self.headers.update({"Cookie": cookie})
        if not cookie:
            self.headers.pop("Cookie")

    def empty_cache(self, name=None):  # empty all the cache by default
        if not name:
            self.cache = dict()
            return
        if not self.cache.get(name):
            print("Name not found! Aborting...")
            return
        self.cache.pop(name)

    def get_hot_news(self, **kwargs):
        country = kwargs.get('country', 'us') or "us"  # (no "country" in kwargs) or (country=None)
        category = kwargs.get('category', 'general') or "general"
        # if news is not cached, or cache has expired, update cache
        if not (news := self.cache["news"].get(key := (country, category))) or \
                news["expires"] < datetime.datetime.utcnow():
            url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&" \
                  "apiKey=9d51c192354848748d129b08faea32ea"
            res = self.session.get(url, headers=self.headers)
            data = res.json()
            num = kwargs["num"]
            self.cache["news"][key] = {"articles": data["articles"][:num],
                                       "expires": datetime.datetime.utcnow() + datetime.timedelta(
                                           seconds=kwargs["freq"])}
        return self.cache["news"][key]["articles"]

    def weibo_hot_search(self, **kwargs):  # cache not applied because change is rapid
        # Juncheng's cookie
        self.set_cookie('SINAGLOBAL=9266532810528.248.1599373736944; login_sid_t=b3eea3454137ac70848c4a32a25c282a; '
                        'cross_origin_proto=SSL; _s_tentry=-; Apache=349928957021.5636.1618803988393; '
                        'ULV=1618803988399:9:2:1:349928957021.5636.1618803988393:1617765463404; '
                        'wb_view_log=1536*8641.25&1920*10802.0000000298023224; ALF=1650340136; '
                        'SSOLoginState=1618804137; '
                        'SUB'
                        '=_2A25NeI38DeRhGeFN71AZ9y7Nwj2IHXVuD_g0rDV8PUNbmtANLVLmkW9NQDBJhXO328RvICGNnS19JPY6LqASfZKJ; '
                        'SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhfZk1zy.rnRggXMDx9zNI55JpX5KzhUgL'
                        '.FoM0ShzRS05p1K22dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNe0BE1hM7eK.p; wvr=6; '
                        'wb_view_log_7342870191=1536*8641.25&1920*10802.0000000298023224; UOR=www.baidu.com,'
                        'weibo.com,www.baidu.com; webim_unReadCount={"time":1618804704383,"dm_pub_total":0,'
                        '"chat_group_client":0,"chat_group_notice":0,"allcountNum":11,"msgbox":0}')
        res = self.session.get("https://s.weibo.com/top/summary?Refer=top_hot&topnav=1&wvr=6", headers=self.headers)
        selectors = [f"#pl_top_realtimehot > table > tbody > tr:nth-child({i}) > td.td-02 > a"
                     for i in range(2, 2 + int(kwargs["num"]))]
        top_list = []
        for s in selectors:
            element = res.html.find(s, first=True)
            top_list.append({"url": "https://s.weibo.com" + element.attrs["href"], "title": element.text})
        return top_list

    def get_cookie(self, domain="localhost", port=80, uname="U1", password="111"):
        cached_cookies = self.cache.get("cookies")
        if cached_cookies:
            if cached_cookies.get(uname):
                return cached_cookies[uname]

        url = f"http://{domain}:{port}/api/auth/login"
        res = self.session.post(url, data={"uname": uname, "password": password}, headers=self.headers)
        cookie = res.headers["Set-Cookie"].split(";")[0]

        if not cached_cookies:
            self.cache["cookies"] = dict()
        self.cache["cookies"].update({uname: cookie})
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


class scrapperFactory:

    @staticmethod
    def produce(sync=True):
        return OTSpider() if sync else AsyncOTSpider()


OT_spider = scrapperFactory.produce()

if __name__ == '__main__':
    # news = OT_spider.get_hot_news(num=3, freq=60)
    # print(news)
    # print(async_spider.run_multitask(async_spider.get_baidu))
    # OT_spider.upload_avatar(port=5000)
    print(OT_spider.weibo_hot_search(num=10))
