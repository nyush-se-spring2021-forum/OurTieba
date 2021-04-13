from project import *

app = create_app()


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
    return response


@app.route("/test")
def sql_test():
    A = Admin(password="root", aname="root", timestamp="2000-01-01 00:00:00")

    u1 = User(uname="U1", password="111", nickname="user1", timestamp="2020-12-25 10:00:00")
    u2 = User(uname="U2", password="222", nickname="user2", timestamp="2020-12-26 08:00:00")
    u3 = User(uname="U3", password="333", nickname="user3", timestamp="2020-12-27 19:00:00")
    u4 = User(uname="U4", password="444", nickname="user4", timestamp="2020-12-28 20:00:00")
    u5 = User(uname="U5", password="555", nickname="user5", timestamp="2020-12-29 13:00:00")
    u6 = User(uname="U6", password="666", nickname="user6", timestamp="2020-12-30 17:00:00",
              banned=1, banDuration="2022-01-01 00:00:00")

    b1 = Board(name="B1", hot=100, viewCount=15, subscribeCount=1, timestamp="2020-12-30 09:00:00",
               postCount=3)
    b2 = Board(name="B2", hot=50, viewCount=5, timestamp="2020-12-31 09:00:00", postCount=1)
    b3 = Board(name="B3", hot=120, viewCount=25, subscribeCount=1, timestamp="2021-02-01 10:40:00",
               postCount=5)
    b4 = Board(name="B4", hot=0, timestamp="2020-08-30 18:00:00", postCount=0)
    b5 = Board(name="B5", hot=80, viewCount=12, timestamp="2021-01-30 09:30:00", postCount=2)
    b6 = Board(name="B6", hot=70, viewCount=10, timestamp="2020-10-29 10:05:00", postCount=2)

    p1 = Post(Uid=1, Bid=1, title="P1", content="111", viewCount=40, timestamp="2020-12-30 10:00:00",
              commentCount=12, LCT="2021-03-21 09:00:00", dislikeCount=1)
    p2 = Post(Uid=2, Bid=1, title="P2", content="222", timestamp="2021-01-30 15:00:00")
    p3 = Post(Uid=3, Bid=1, title="P3", content="333", timestamp="2021-02-03 20:40:00")
    p4 = Post(Uid=5, Bid=2, title="P4", content="444", timestamp="2021-03-20 10:50:00")
    p5 = Post(Uid=1, Bid=3, title="P5", content="555", timestamp="2021-02-02 10:40:00")
    p6 = Post(Uid=3, Bid=3, title="P6", content="666", timestamp="2021-02-02 16:00:00")
    p7 = Post(Uid=4, Bid=3, title="P7", content="777", viewCount=1, timestamp="2021-03-10 10:40:00", likeCount=1)
    p8 = Post(Uid=4, Bid=3, title="P8", content="888", timestamp="2021-03-12 06:02:00")
    p9 = Post(Uid=1, Bid=3, title="P9", content="999", timestamp="2021-03-15 19:30:00")
    p10 = Post(Uid=2, Bid=5, title="P10", content="1010", timestamp="2021-02-04 15:00:00")
    p11 = Post(Uid=5, Bid=5, title="P11", content="1111", viewCount=3, timestamp="2021-03-22 23:00:00",
               commentCount=1, LCT="2021-03-23 13:03:00")
    p12 = Post(Uid=2, Bid=6, title="P12", content="1212", timestamp="2020-11-06 08:42:00")
    p13 = Post(Uid=2, Bid=6, title="P13", content="1313", timestamp="2021-03-21 12:01:00")

    c1 = Comment(Uid=6, Pid=1, content="wtf", timestamp="2021-01-01 02:00:00", dislikeCount=1)
    c2 = Comment(Uid=1, Pid=1, content="c111", timestamp="2021-01-01 09:00:00")
    c3 = Comment(Uid=2, Pid=1, content="c222", timestamp="2021-01-02 09:00:00")
    c4 = Comment(Uid=3, Pid=1, content="c333", timestamp="2021-01-05 09:00:00")
    c5 = Comment(Uid=4, Pid=1, content="c444", timestamp="2021-01-21 09:00:00")
    c6 = Comment(Uid=5, Pid=1, content="c555", timestamp="2021-02-13 09:00:00")
    c7 = Comment(Uid=2, Pid=1, content="c666", timestamp="2021-03-01 09:00:00", likeCount=1)
    c8 = Comment(Uid=3, Pid=1, content="c777", timestamp="2021-03-05 09:00:00")
    c9 = Comment(Uid=4, Pid=1, content="c888", timestamp="2021-03-08 09:00:00")
    c10 = Comment(Uid=5, Pid=1, content="c999", timestamp="2021-03-11 09:00:00")
    c11 = Comment(Uid=1, Pid=1, content="c1010", timestamp="2021-03-20 09:00:00")
    c12 = Comment(Uid=2, Pid=1, content="c1111", timestamp="2021-03-21 09:00:00")
    c13 = Comment(Uid=5, Pid=11, content="c1212", timestamp="2021-03-23 13:03:00")

    r1 = Report(Uid=1, target="comment", targetId=1, reason="yin zhan", timestamp="2021-01-01 09:05:00")
    r2 = Report(Uid=2, target="comment", targetId=1, reason="yin zhan!", timestamp="2021-01-02 09:05:00")
    r3 = Report(Uid=5, target="post", targetId=5, reason="dunno", timestamp="2021-02-03 10:40:00")

    cs1 = CommentStatus(Uid=1, Cid=1, liked=0, disliked=1, lastModified="2021-01-01 09:04:00")
    cs2 = CommentStatus(Uid=2, Cid=7, liked=1, disliked=0, lastModified="2021-03-02 11:00:00")

    ps1 = PostStatus(Uid=6, Pid=1, liked=0, disliked=1, lastModified="2021-01-01 01:59:00")
    ps2 = PostStatus(Uid=5, Pid=7, liked=1, disliked=0, lastModified="2021-03-10 12:00:00")

    s1 = Subscription(Uid=1, Bid=1, subscribed=1, lastModified="2020-12-30 09:00:00")
    s2 = Subscription(Uid=4, Bid=3, subscribed=1, lastModified="2021-02-03 14:50:00")

    my_db.add(A)
    for u in [u1, u2, u3, u4, u5, u6]:
        my_db.add(u)

    for b in [b1, b2, b3, b4, b5, b6]:
        my_db.add(b)

    for p in [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13]:
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

    return "success!", 200


@app.route('/frontendtest')
def frontendtest():
    abort(500)


@app.route("/getsomething")
def getsth():
    John = my_db.query(User, User.Uid == 1, first=True)
    uname = John.uname
    return jsonify({"data": [{"name": uname}]})


if __name__ == '__main__':
    app.run()
