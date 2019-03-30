from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_github import GitHub
from flask_dotenv import DotEnv

env = DotEnv()
bootstrap = Bootstrap()
moment = Moment()
github = GitHub()

def create_app():
    app = Flask(__name__)
    env.init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    github.init_app(app)

    app.secret_key = app.config["SECRET_KEY"]

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
