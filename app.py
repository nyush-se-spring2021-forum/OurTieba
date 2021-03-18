from project import *

app = create_app()


@app.route('/')
def hello():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
