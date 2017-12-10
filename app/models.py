#-*-coding:utf-8-*-
from datetime import datetime
from . import db, login_manager, create_app
from app import app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown2 import markdown


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ["title", "subtitle", "body_text"]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    subtitle = db.Column(db.String(128))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    content_md = db.Column(db.Text)
    content_html = db.Column(db.Text)
    views = db.Column(db.Integer, default=0)
    abstract = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.now)
    modified_time = db.Column(db.DateTime, default=datetime.now)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '{0}(id={1})'.format(self.__class__.__name__, self.id)

    @staticmethod
    def generate_markdown(md):
        return markdown(md, extras=["fenced-code-blocks", "code-friendly", "header-ids"])


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    posts = db.relationship("Post", backref="tag", lazy="dynamic")


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128), default="abc@gmail.com")
    avatar = db.Column(db.LargeBinary(length=2048))
    date_join = db.Column(db.DateTime, index=True, default=datetime.now)
    introduction = db.Column(db.Text)
    posts = db.relationship("Post", backref="author", lazy="dynamic")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.LargeBinary(length=2048))

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})


class VisitRecord(db.Model):
    __tablename__ = "visitrecords"
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(64), index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    visit_time = db.Column(db.DateTime, index=True, default=datetime.now)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
