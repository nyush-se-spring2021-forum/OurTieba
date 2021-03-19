from project import *

app = create_app()


@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/test")
def add_user():
    u1 = User("secret", "John")
    u2 = User("guess", "Bob")
    db_session.add(u1)
    db_session.add(u2)
    db_session.commit()

    p = Post(1, "AA", "bbb")
    db_session.add(p)
    db_session.commit()

    John = db_session.query(User).filter(User.Uid == 1).first()
    print(John.posts.title)

    db_session.close()
    return "success!", 200


if __name__ == '__main__':
    app.run()
