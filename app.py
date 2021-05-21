import sys

from ourtieba import create_app

env = "production" if len(sys.argv) == 1 or sys.argv[1] != "--dev" else "development"

app = create_app(env)


if __name__ == '__main__':
    app.run()
