import datetime

from requests_html import HTMLSession, AsyncHTMLSession


class OTSpider:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self._session = HTMLSession()
        self._headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                      "like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57"}
        self.cache = {"news": dict()}  # note that this is stateless, which means it is cleared on every restart
        self.base_url = None

    def get(self, *arg, headers=None, **kwargs):
        if headers is None:
            headers = self._headers
        if self.base_url:
            return self._session.get(self.base_url + arg[0], headers=headers, **kwargs)
        return self._session.get(*arg, headers=headers, **kwargs)

    def post(self, *arg, headers=None, **kwargs):
        if headers is None:
            headers = self._headers
        if self.base_url:
            return self._session.post(self.base_url + arg[0], headers=headers, **kwargs)
        return self._session.post(*arg, headers=headers, **kwargs)

    def head(self, *arg, headers=None, **kwargs):
        if headers is None:
            headers = self._headers
        if self.base_url:
            return self._session.head(self.base_url + arg[0], headers=headers, **kwargs)
        return self._session.head(*arg, headers=headers, **kwargs)

    def delete(self, *arg, headers=None, **kwargs):
        if headers is None:
            headers = self._headers
        if self.base_url:
            return self._session.delete(self.base_url + arg[0], headers=headers, **kwargs)
        return self._session.delete(*arg, headers=headers, **kwargs)

    def options(self, *arg, headers=None, **kwargs):
        if headers is None:
            headers = self._headers
        if self.base_url:
            return self._session.options(self.base_url + arg[0], headers=headers, **kwargs)
        return self._session.options(*arg, headers=headers, **kwargs)

    def put(self, *arg, headers=None, **kwargs):
        if headers is None:
            headers = self._headers
        if self.base_url:
            return self._session.put(self.base_url + arg[0], headers=headers, **kwargs)
        return self._session.put(*arg, headers=headers, **kwargs)

    def set_headers(self, headers, append=False):  # append means whether to add to headers instead of overwriting it
        if append:
            return self._headers.update(headers)
        self._headers = headers

    def set_cookie(self, cookie):  # if cookie set to None, remove cookie
        self._headers.update({"Cookie": cookie})
        if not cookie:
            self._headers.pop("Cookie")

    def empty_cache(self, name=None):  # empty all the cache by default
        if not name:
            self.cache = dict()
            return
        if not self.cache.get(name):
            print("Name not found! Aborting...")
            return
        self.cache.pop(name)

    def get_hot_news(self, **kwargs):
        # if news is not cached, or cache has expired, update cache
        if not self.cache.get("news") or self.cache["news"]["expires"] < datetime.datetime.utcnow():
            url = "https://newsapi.org/v2/top-headlines?country=us&category=general&" \
                  "apiKey=9d51c192354848748d129b08faea32ea"
            res = self._session.get(url, headers=self._headers)
            data = res.json()
            num = kwargs["num"]
            self.cache["news"] = {"articles": data["articles"][:num],
                                  "expires": datetime.datetime.utcnow() + datetime.timedelta(seconds=kwargs["freq"])}
        return self.cache["news"]["articles"]

    def close(self):
        self._session.close()


class scrapperFactory:

    @staticmethod
    def produce():
        return OTSpider()


OT_spider = scrapperFactory.produce()

if __name__ == '__main__':
    news = OT_spider.get_hot_news(num=3, freq=60)
    print(news)
