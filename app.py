from project import *

app = create_app()


@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/add_user")
def add_user():
    u = User(Uid="0003", password="all")
    db_session.add(u)
    db_session.commit()
    return "success!", 200


if __name__ == '__main__':
    app.run()
