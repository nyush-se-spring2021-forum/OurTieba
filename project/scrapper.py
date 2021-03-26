from requests_html import HTMLSession

session = HTMLSession()


def get_hot_news(**kwargs):
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=9d51c192354848748d129b08faea32ea"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57"}
    res = session.get(url, headers=headers)
    data = res.json()
    num = kwargs["num"]
    return data["articles"][:num]


if __name__ == '__main__':
    get_hot_news()
