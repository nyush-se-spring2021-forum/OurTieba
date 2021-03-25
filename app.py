from project import *

app = create_app()


@app.teardown_appcontext
def teardown_session(e):
    DB_session.remove()


@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/test")
def sql_test():
    u1 = User("secret", "John")
    u2 = User("guess", "Bob")
    db_session.add(u1)
    db_session.add(u2)
    db_session.commit()

    count = db_session.query(func.count(User.Uid)).scalar()
    print(f"There are {count} users.")

    p = Post(1, "AA", "bbb")
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
