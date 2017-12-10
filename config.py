#-*-coding:utf-8-*-
# from jieba.analyse import ChineseAnalyzer
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASK_EMAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASK_EMAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    UPLOAD_FOLDER = "/uploads"
    ALLOWED_EXTENSIONS = set(['png', "jpeg", "gif", "jpg"])
    # MSEARCH_INDEX_NAME = 'whoosh_index'
    # # simple,whoosh
    # MSEARCH_BACKEND = 'whoosh'
    # # auto create or update index
    # MSEARCH_ENABLE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # DEV_DATABASE_URL = "mysql://root:138049@localhost:3306/data_blog"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # SQLALCHEMY_DATABASE_URI = os.environ.get(
    #     'DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_DATABASE_URI = "mysql://root:138049@localhost/data_blog"
    # WHOOSH_BASE = os.path.join(basedir, 'search.db')
    # MAX_SEARCH_RESULTS = 50


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
