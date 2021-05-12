from flask import Flask
from flask_moment import Moment

from .configs import *  # import configurations
from .database import *  # import database session
from .logger import *  # import logger
from .models import *  # import all the models
from .scheduler import *  # import scheduler
from .scrapper import *  # import scrapper
from .views import *  # import all the view


def create_app():
    app = Flask(__name__, static_url_path="/")
    config_app(app)

    with app.app_context():
        Moment(app)
        init_db()
        register_blue(app)

        # init_logger()
        # init_scheduler(app)
    @app.teardown_appcontext
    def teardown_session(e):
        my_db.close()
        OT_spider.close()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template("error/403.html"), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("error/500.html"), 500

    @app.before_request
    def filter_request():
        if request.method not in ALLOWED_METHODS:
            return "Bad method", 403
        ua = str(request.user_agent)
        if "Mozilla" not in ua or "Gecko" not in ua:
            return "No Scrappers!", 403

    @app.after_request
    def set_res_headers(response):
        response.headers["Server"] = "OurTieba"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "sameorigin"
        return response

    @app.template_filter("index_format")
    def add_zeros(i, length):  # format index in photos.html
        """
        Pad zeros to i, and turn it into a string. The length is at least 2.
        :param i: int. Integer to pad.
        :param length: int. Base integer.
        :return: A padded string.

        For example,
        add_zeros(1, 2) -> "01";
        add_zeros(1, 12) -> "01";
        add_zeros(13, 101) -> "013".
        """
        return ("{:0>" + str(max(len(str(length)), 2)) + "d}").format(i)

    if app.config['ENV'] == 'development':
        @app.route("/test")
        def sql_test():
            A = Admin(password="root", aname="root", timestamp="2000-01-01 00:00:00")

            u1 = User(uname="U1", password="111", nickname="user1", timestamp="2020-12-25 10:00:00",
                      avatar="avatar/-2837748924044579792.png")
            u2 = User(uname="U2", password="222", nickname="user2", timestamp="2020-12-26 08:00:00")
            u3 = User(uname="U3", password="333", nickname="user3", timestamp="2020-12-27 19:00:00")
            u4 = User(uname="U4", password="444", nickname="user4", timestamp="2020-12-28 20:00:00")
            u5 = User(uname="U5", password="555", nickname="user5", timestamp="2020-12-29 13:00:00")
            u6 = User(uname="U6", password="666", nickname="user6", timestamp="2020-12-30 17:00:00",
                      banned=1, banDuration="2022-01-01 00:00:00")

            b1 = Board(name="B1", hot=100, viewCount=15, subscribeCount=1, timestamp="2020-12-30 09:00:00",
                       postCount=3, sticky_on_top=20, description="D1")
            b2 = Board(name="B2", hot=50, viewCount=5, timestamp="2020-12-31 09:00:00", postCount=1,
                       description="D2")
            b3 = Board(name="B3", hot=120, viewCount=25, subscribeCount=1, timestamp="2021-02-01 10:40:00",
                       postCount=5, description="D3")
            b4 = Board(name="B4", hot=0, timestamp="2020-08-30 18:00:00", postCount=0, description="D4")
            b5 = Board(name="B5", hot=80, viewCount=12, timestamp="2021-01-30 09:30:00", postCount=2,
                       sticky_on_top=10, description="D5")
            b6 = Board(name="B6", hot=70, viewCount=10, timestamp="2020-10-29 10:05:00", postCount=2,
                       description="D6")

            p1 = Post(Uid=1, Bid=1, title="P1", content="<p>111</p>", viewCount=40, timestamp="2020-12-30 10:00:00",
                      commentCount=12, LCT="2021-03-21 09:00:00", dislikeCount=1, text="111", available_floor=14)
            p2 = Post(Uid=2, Bid=1, title="P2", content="<p>222</p>", timestamp="2021-01-30 15:00:00", text="222")
            p3 = Post(Uid=3, Bid=1, title="P3", content="<p>333</p>", timestamp="2021-02-03 20:40:00", text="333")
            p4 = Post(Uid=5, Bid=2, title="P4", content="<p>444</p>", timestamp="2021-03-20 10:50:00", text="444")
            p5 = Post(Uid=1, Bid=3, title="P5", content="<p>555</p>", timestamp="2021-02-02 10:40:00", text="555")
            p6 = Post(Uid=3, Bid=3, title="P6", content="<p>666</p>", timestamp="2021-02-02 16:00:00", text="666")
            p7 = Post(Uid=4, Bid=3, title="P7", content="<p>777</p>", viewCount=1, timestamp="2021-03-10 10:40:00",
                      likeCount=1, text="777")
            p8 = Post(Uid=4, Bid=3, title="P8", content="<p>888</p>", timestamp="2021-03-12 06:02:00", text="888")
            p9 = Post(Uid=1, Bid=3, title="P9", content="<p>999</p>", timestamp="2021-03-15 19:30:00", text="999")
            p10 = Post(Uid=2, Bid=5, title="P10", content="<p>1010</p>", timestamp="2021-02-04 15:00:00",
                       text="1010")
            p11 = Post(Uid=5, Bid=5, title="P11", content="<p>1111</p>", viewCount=3,
                       timestamp="2021-03-22 23:00:00",
                       commentCount=1, LCT="2021-03-23 13:03:00", text="1111", available_floor=3)
            p12 = Post(Uid=2, Bid=6, title="P12", content="<p>1212</p>", timestamp="2020-11-06 08:42:00",
                       text="1212")
            p13 = Post(Uid=2, Bid=6, title="P13", content="<p>1313</p>", timestamp="2021-03-21 12:01:00",
                       text="1313")
            p14 = Post(Uid=2, Bid=1, title="P14", content="<p>1414</p>", timestamp="2021-03-21 12:01:10",
                       text="1414")
            p15 = Post(Uid=2, Bid=1, title="P15", content="<p>1515</p>", timestamp="2021-03-21 12:01:00",
                       text="1515")
            p16 = Post(Uid=2, Bid=1, title="P16", content="<p>1616</p>", timestamp="2021-03-21 12:01:00",
                       text="1616")
            p17 = Post(Uid=2, Bid=1, title="P17", content="<p>1717</p>", timestamp="2021-03-21 12:01:00",
                       text="1717")
            p18 = Post(Uid=2, Bid=1, title="P18", content="<p>1818</p>", timestamp="2021-03-21 12:01:00",
                       text="1818")
            p19 = Post(Uid=2, Bid=1, title="P19", content="<p>1919</p>", timestamp="2021-03-21 12:01:00",
                       text="1919")
            p20 = Post(Uid=2, Bid=1, title="Game Visual", content='<p>Found on official twitter account:<br/>'
                                                                  '<img class="OT_image" src="/cdn/photo/-3701751787780283978'
                                                                  '.jpeg" title="" alt=""/></p>',
                       medias=["photo/-3701751787780283978.jpeg"],
                       timestamp="2021-05-05 08:11:11", text='Found on official twitter account:')
            p21 = Post(Uid=1, Bid=1, title="Edel Lilie Last Bullet Remix", content='<p>Song in the video below. '
                                                                                   'Enjoy~<br/><iframe class="OT_video '
                                                                                   'OT_iframe" width="420" height="280" '
                                                                                   'src="/play?src=/cdn/video'
                                                                                   '/-7344473432041877746.webm"></iframe><br'
                                                                                   '/>Here&#39;s the cover:<br/><img '
                                                                                   'class="OT_image" '
                                                                                   'src="/cdn/photo/-1976482922365202782.jpeg'
                                                                                   '" title="" alt=""/></p>',
                       text="Song in the video below. Enjoy~Here's the cover:", timestamp="2021-05-06 13:06:35",
                       medias=["video/-7344473432041877746.webm", "photo/-1976482922365202782.jpeg"])

            c1 = Comment(Uid=6, Pid=1, content="<p>wtf</p>", timestamp="2021-01-01 02:00:00", dislikeCount=1,
                         text="wtf", floor=2)
            c2 = Comment(Uid=1, Pid=1, content="<p>c111</p>", timestamp="2021-01-01 09:00:00", text="c111", floor=3)
            c3 = Comment(Uid=2, Pid=1, content="<p>c222</p>", timestamp="2021-01-02 09:00:00", text="c222", floor=4)
            c4 = Comment(Uid=3, Pid=1, content="<p>c333</p>", timestamp="2021-01-05 09:00:00", text="c333", floor=5)
            c5 = Comment(Uid=4, Pid=1, content="<p>c444</p>", timestamp="2021-01-21 09:00:00", text="c444", floor=6)
            c6 = Comment(Uid=5, Pid=1, content="<p>c555</p>", timestamp="2021-02-13 09:00:00", text="c555", floor=7)
            c7 = Comment(Uid=2, Pid=1, content="<p>c666</p>", timestamp="2021-03-01 09:00:00", likeCount=1,
                         text="c666", floor=8)
            c8 = Comment(Uid=3, Pid=1, content="<p>c777</p>", timestamp="2021-03-05 09:00:00", text="c777", floor=9)
            c9 = Comment(Uid=4, Pid=1, content="<p>c888</p>", timestamp="2021-03-08 09:00:00", text="c888",
                         floor=10)
            c10 = Comment(Uid=5, Pid=1, content="<p>c999</p>", timestamp="2021-03-11 09:00:00", text="c999",
                          floor=11)
            c11 = Comment(Uid=1, Pid=1, content="<p>c1010</p>", timestamp="2021-03-20 09:00:00", text="c1010",
                          floor=12)
            c12 = Comment(Uid=2, Pid=1, content="<p>c1111</p>", timestamp="2021-03-21 09:00:00", text="c1111",
                          floor=13)
            c13 = Comment(Uid=5, Pid=11, content="<p>c1212</p>", timestamp="2021-03-23 13:03:00", text="c1212",
                          floor=2)

            r1 = Report(Uid=1, target="comment", targetId=1, reason="yin zhan", timestamp="2021-01-01 09:05:00")
            r2 = Report(Uid=2, target="comment", targetId=1, reason="yin zhan!", timestamp="2021-01-02 09:05:00")
            r3 = Report(Uid=5, target="post", targetId=5, reason="dunno", timestamp="2021-02-03 10:40:00")

            cs1 = CommentStatus(Uid=1, Cid=1, liked=0, disliked=1, lastModified="2021-01-01 09:04:00")
            cs2 = CommentStatus(Uid=2, Cid=7, liked=1, disliked=0, lastModified="2021-03-02 11:00:00")

            ps1 = PostStatus(Uid=6, Pid=1, liked=0, disliked=1, lastModified="2021-01-01 01:59:00")
            ps2 = PostStatus(Uid=5, Pid=7, liked=1, disliked=0, lastModified="2021-03-10 12:00:00")

            s1 = Subscription(Uid=1, Bid=1, subscribed=1, lastModified="2020-12-30 09:00:00")
            s2 = Subscription(Uid=4, Bid=3, subscribed=1, lastModified="2021-02-03 14:50:00")

            h1 = History(Uid=1, Pid=1, lastVisitTime="2021-04-01 16:00:59")
            h2 = History(Uid=1, Pid=21, lastVisitTime="2021-03-24 18:00:59")
            h3 = History(Uid=2, Pid=3, lastVisitTime="2021-02-04 08:45:32")

            my_db.add(A)
            for u in [u1, u2, u3, u4, u5, u6]:
                my_db.add(u)

            for b in [b1, b2, b3, b4, b5, b6]:
                my_db.add(b)

            for p in [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20,
                      p21]:
                my_db.add(p)

            for c in [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13]:
                my_db.add(c)

            for r in [r1, r2, r3]:
                my_db.add(r)

            for (uid, rid) in zip([1, 2, 5], [1, 2, 3]):
                u = my_db.query(User, User.Uid == uid, first=True)
                r = my_db.query(Report, Report.Rid == rid, first=True)
                u.reports.append(r)

            for s in [cs1, cs2, ps1, ps2]:
                my_db.add(s)

            for sub in [s1, s2]:
                my_db.add(sub)

            for history in [h1, h2, h3]:
                my_db.add(history)

            return "success!", 200
    return app
