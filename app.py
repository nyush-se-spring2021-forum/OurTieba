from project import *

app = create_app()


@app.teardown_appcontext
def teardown_session(e):
    DB_session.remove()


@app.route('/')
def hello():
    hot_articles = get_hot_news(num=RECOMMEND_NUM_NEWS)
    hot_news = [{"title": a["title"], "abstract": a["description"], "link": a["url"],
                 "img_src": a["urlToImage"]} for a in hot_articles]
    boards = db_session.query(Board).order_by(Board.hot.desc()).all()[:RECOMMEND_NUM_BOARD]
    recommend_boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount} for b in boards]
    data = {"boards": recommend_boards, "news": hot_news}
    db_session.commit()
    return render_template("index.html", data=data)


@app.route("/board/<Bid>")
def get_posts_in_board(Bid):
    b = db_session.query(Board).filter(Board.Bid == Bid).all()
    if len(b) == 0:
        return "Not Found!", 404
    board_info = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount, "time": b.timestamp}]

    order = request.args.get("order", "latest_comment")
    page = request.args.get("page", "1")
    if order == "latest_comment":
        order = Post.latestCommentTime.desc()
    elif order == "newest":
        order = Post.timestamp.desc()
    elif order == "like_count":
        order = Post.likeCount.desc()
    else:
        order = Post.commentCount.desc()

    posts_match_result = db_session.query(Post).filter(Post.Bid == Bid).order_by(order).all()
    num_match = len(posts_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    posts = [{"Pid": p.Pid, "title": p.title, "summary": p.content[:100] + '...', "publish_time": p.timestamp,
              "comment_count": p.commentCount, "like_count": p.likeCount, "dislike_count": p.dislikeCount}
             for p in posts_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "posts": posts, "board_info": board_info}

    db_session.commit()
    return render_template("board.html", data=data)


@app.route("/board/create")
def create_post():
    Bid = request.args.get("Bid")
    if not Bid or not Bid.isnumeric():
        return jsonify({"error": {"msg": "invalid data"}}), 404
    Uid = session.get("Uid")
    data = {"Bid": Bid}
    if not Uid:
        return render_template("create.html", data=data, error="Not logged in!")
    match_board = db_session.query(Board).filter(Board.Bid == Bid).all()
    if not match_board:
        return jsonify({"error": {"msg": "invalid board ID"}}), 404
    return render_template("create.html", data=data)


@app.route("/search_board")
def search_board():
    keyword = request.args.get("kw")
    if not keyword:
        return render_template("search_result.html", error="Please enter a keyword!")
    order = request.args.get("order", "popular")
    page = request.args.get("page", "1")
    order = Board.timestamp.desc() if order == "popular" else Board.hot.desc()
    match_result = db_session.query(Board).filter(Board.name.like("%" + keyword + "%")).order_by(order).all()
    num_match = len(match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    boards = [{"Bid": b.Bid, "name": b.name, "hot": b.hot, "post_count": b.postCount}
              for b in match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "boards": boards}
    db_session.commit()
    return render_template("search_result.html", data=data)


@app.route("/post/<Pid>")
def get_comments_in_post(Pid):
    p = db_session.query(Post).filter(Post.Pid == Pid).all()
    if len(p) == 0:
        return "Not Found", 404
    post_info = [{"Pid": p.Pid, "title": p.title, "content": p.content, "publish_time": p.timestamp,
                  "comment_count": p.commentCount, "like_count": p.likeCount, "dislike_count": p.dislikeCount,
                  "owner": p.owner.nickname, "avatar": p.owner.avatar}]

    order = request.args.get("order", "most_like")
    page = request.args.get("page", "1")

    order = Comment.likeCount.desc() if order == "most_like" else Comment.timestamp.desc()
    comment_match_result = db_session.query(Comment).filter(Comment.Pid == Pid).order_by(order).all()
    num_match = len(comment_match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    Comments = [{"Cid": c.Cid, "content": c.content, "publish_time": c.timestamp, "like_count": c.likeCount,
                 "dislike_count": c.dislikeCount, "publish_user": c.comment_by.nickname,
                 "user_avatar": c.comment_by.avatar}
                for c in comment_match_result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "comments": Comments, "post_info": post_info}
    db_session.commit()
    return render_template("post.html", data=data)


@app.route("/report")
def report():
    target = request.args.get("target", 0)
    id = request.args.get("id")
    data = {"id": id, "target": target}
    if target == "comment":
        match_result = db_session.query(Comment).filter(Comment.Cid == id).all()
        if len(match_result) == 0:
            return "Not Found", 404
        return render_template("report.html", data=data)
    elif target == "post":
        match_result = db_session.query(Post).filter(Post.Pid == id).all()
        if len(match_result) == 0:
            return "Not Found", 404
        return render_template("report.html", data=data)
    else:
        return "Invalid URL", 404


@app.route("/test")
def sql_test():
    u1 = User(uname="U1", password="111", nickname="user1")
    u2 = User(uname="U2", password="222", nickname="user2")
    u3 = User(uname="U3", password="333", nickname="user3")
    u4 = User(uname="U4", password="444", nickname="user4")
    u5 = User(uname="U5", password="555", nickname="user5")

    b1 = Board(name="B1", hot=100, timestamp="2020-12-30 09:00:00", postCount=3)
    b2 = Board(name="B2", hot=50, timestamp="2020-12-31 09:00:00", postCount=1)
    b3 = Board(name="B3", hot=120, timestamp="2021-02-01 10:40:00", postCount=5)
    b4 = Board(name="B4", hot=0, timestamp="2020-08-30 18:00:00", postCount=0)
    b5 = Board(name="B5", hot=80, timestamp="2021-01-30 09:30:00", postCount=2)
    b6 = Board(name="B6", hot=70, timestamp="2020-10-29 10:05:00", postCount=2)

    p1 = Post(Uid=1, Bid=1, title="P1", content="111", timestamp="2020-12-30 10:00:00", commentCount=11,
              LCT="2021-03-21 09:00:00")
    p2 = Post(Uid=2, Bid=1, title="P2", content="222", timestamp="2021-01-30 15:00:00")
    p3 = Post(Uid=3, Bid=1, title="P3", content="333", timestamp="2021-02-03 20:40:00")
    p4 = Post(Uid=5, Bid=2, title="P4", content="444", timestamp="2021-03-20 10:50:00")
    p5 = Post(Uid=1, Bid=3, title="P5", content="555", timestamp="2021-02-02 10:40:00")
    p6 = Post(Uid=3, Bid=3, title="P6", content="666", timestamp="2021-02-02 16:00:00")
    p7 = Post(Uid=4, Bid=3, title="P7", content="777", timestamp="2021-03-10 10:40:00")
    p8 = Post(Uid=4, Bid=3, title="P8", content="888", timestamp="2021-03-12 06:02:00")
    p9 = Post(Uid=1, Bid=3, title="P9", content="999", timestamp="2021-03-15 19:30:00")
    p10 = Post(Uid=2, Bid=5, title="P10", content="1010", timestamp="2021-02-04 15:00:00")
    p11 = Post(Uid=5, Bid=5, title="P11", content="1111", timestamp="2021-03-22 23:00:00", commentCount=1,
               LCT="2021-03-23 13:03:00")
    p12 = Post(Uid=2, Bid=6, title="P12", content="1212", timestamp="2020-11-06 08:42:00")
    p13 = Post(Uid=2, Bid=6, title="P13", content="1313", timestamp="2021-03-21 12:01:00")

    c1 = Comment(Uid=1, Pid=1, content="c111", timestamp="2021-01-01 09:00:00")
    c2 = Comment(Uid=2, Pid=1, content="c222", timestamp="2021-01-02 09:00:00")
    c3 = Comment(Uid=3, Pid=1, content="c333", timestamp="2021-01-05 09:00:00")
    c4 = Comment(Uid=4, Pid=1, content="c444", timestamp="2021-01-21 09:00:00")
    c5 = Comment(Uid=5, Pid=1, content="c555", timestamp="2021-02-13 09:00:00")
    c6 = Comment(Uid=2, Pid=1, content="c666", timestamp="2021-03-01 09:00:00")
    c7 = Comment(Uid=3, Pid=1, content="c777", timestamp="2021-03-05 09:00:00")
    c8 = Comment(Uid=4, Pid=1, content="c888", timestamp="2021-03-08 09:00:00")
    c9 = Comment(Uid=5, Pid=1, content="c999", timestamp="2021-03-11 09:00:00")
    c10 = Comment(Uid=1, Pid=1, content="c1010", timestamp="2021-03-20 09:00:00")
    c11 = Comment(Uid=2, Pid=1, content="c1111", timestamp="2021-03-21 09:00:00")
    c12 = Comment(Uid=5, Pid=11, content="c1212", timestamp="2021-03-23 13:03:00")

    for u in [u1, u2, u3, u4, u5]:
        db_session.add(u)
    db_session.commit()

    for b in [b1, b2, b3, b4, b5, b6]:
        db_session.add(b)
    db_session.commit()

    for p in [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13]:
        db_session.add(p)
    db_session.commit()

    for c in [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]:
        db_session.add(c)
    db_session.commit()

    db_session.close()
    return "success!", 200


@app.route("/frontendtest")
def frontendtest():
    return render_template("main.html")


@app.route("/getsomething")
def getsth():
    John = db_session.query(User).filter(User.Uid == 1).first()
    uname = John.uname
    db_session.commit()
    db_session.close()
    return jsonify({"data": [{"name": uname}]})


if __name__ == '__main__':
    app.run()
