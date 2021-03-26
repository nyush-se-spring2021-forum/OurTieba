from project import *

app = create_app()


@app.teardown_appcontext
def teardown_session(e):
    DB_session.remove()


@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/search_board")
def search_board():
    keyword = request.args.get("kw")
    if not keyword:
        return render_template("search_result.html", error="Please enter a keyword!")
    order = request.args.get("sort", "popular")
    page = request.args.get("page", "latest")
    order = Board.timestamp.desc() if order == "popular" else Board.hot.desc()
    match_result = db_session.query(Board).filter(Board.name.like("%" + keyword + "%")).order_by(order).all()
    num_match = len(match_result)
    num_page = (num_match - 1) // PAGE_SIZE + 1
    page = 1 if not page.isnumeric() or int(page) <= 0 else int(page) if int(page) <= num_page else num_page
    boards = [{"name": b.name, "hot": b.hot, "post_count": b.postCount}
              for b in match_result[(page-1)*PAGE_SIZE:page*PAGE_SIZE]]
    data = {"num_match": num_match, "num_page": num_page, "page": page, "boards": boards}
    db_session.commit()
    return render_template("search_result.html", data=data)


@app.route("/test")
def sql_test():
    u1 = User("secret", "John")
    u2 = User("guess", "Bob")
    db_session.add(u1)
    db_session.add(u2)
    db_session.commit()

    count = db_session.query(func.count(User.Uid)).scalar()
    print(f"There are {count} users.")

    b1 = Board("Game", hot=100, timestamp="2020-12-30 09:00:00")
    b2 = Board("E-sports", hot=50, timestamp="2020-12-31 09:00:00")
    db_session.add(b1)
    db_session.add(b2)
    db_session.commit()

    p = Post(1, 1, "AA", "bbb")
    db_session.add(p)
    db_session.commit()

    John = db_session.query(User).filter(User.Uid == 1).first()
    print(f"John's posts: {John.posts}")

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
