#-*-coding:utf-8-*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

app = Flask(__name__)
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login'


def datetimeformat(datetime):
    return datetime.strftime("%Y-%m-%d %H:%M:%S")


def wordcounts(string):
    return len(string)


def split_tags(string):
    return string.split(",")


app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['wordcounts'] = wordcounts
app.jinja_env.filters['split_tags'] = split_tags


def create_app(config_name):
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
