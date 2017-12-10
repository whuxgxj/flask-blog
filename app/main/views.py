#-*-encoding:utf-8-*-
from flask import render_template, flash, redirect, session, url_for, request, g, json, Markup, current_app, make_response
from datetime import datetime, timedelta
from . import main
from ..models import *
from forms import SearchForm
from .. import db
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
import base64
# from ..config import MAX_SEARCH_RESULTS


@main.before_request
def before_request():
    if not Category.query.all():
        analytics = Category(name="analytics")
        football = Category(name="football")
        military = Category(name="military")
        db.session.add_all([analytics, football, military])
        db.session.commit()
    g.search_form = SearchForm()
    g.author = Author
    g.tags = Tag
    g.post = Post
    g.visit = VisitRecord
    g.latest = Post.query.order_by(Post.create_time.desc()).limit(5).all()


@main.route('/', methods=['GET', 'POST'])
@main.route('/blog', methods=['GET', 'POST'])
@main.route('/blog/analytics', methods=['GET', 'POST'])
@main.route('/blog/analytics/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    blogs = Post.query.filter_by(
        category_id=Category.query.filter_by(name="analytics").first().id).order_by(Post.create_time.desc())
    latest = blogs.limit(5).all()
    posts = blogs.paginate(page, 5, False)
    title = u"tomorrow2future | 数据分析"
    return render_template('index.html', posts=posts, latest=latest, title=title)


@main.route('/blog/about', methods=['GET', 'POST'])
def about():
    title = u"tomorrow2future | 关于我们"
    return render_template('about.html', title=title)


@main.route('/blog/military', methods=['GET', 'POST'])
@main.route('/blog/military/<int:page>', methods=['GET', 'POST'])
def military(page=1):
    blogs = Post.query.filter_by(
        category_id=Category.query.filter_by(name="military").first().id).order_by(Post.create_time.desc())
    latest = blogs.limit(5).all()
    posts = blogs.paginate(page, 5, False)
    title = u"tomorrow2future | 军事历史"
    return render_template('index.html', posts=posts, latest=latest, title=title)


@main.route('/blog/football', methods=['GET', 'POST'])
@main.route('/blog/football/<int:page>', methods=['GET', 'POST'])
def football(page=1):
    blogs = Post.query.filter_by(
        category_id=Category.query.filter_by(name="football").first().id).order_by(Post.create_time.desc())
    latest = blogs.limit(5).all()
    posts = blogs.paginate(page, 5, False)
    title = u"tomorrow2future | 足球体育"
    return render_template('index.html', posts=posts, latest=latest, title=title)


@main.route("/blog/post/<article_name>")
def post(article_name):
    post = Post.query.filter_by(title=article_name).first()
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    v = VisitRecord(post_id=post.id, ip_address=ip)
    db.session.add(v)
    post.views = len(
        set([v.ip_address for v in VisitRecord.query.filter_by(post_id=post.id).all()]))
    db.session.add(post)
    db.session.commit()
    title = u"文章 |" + article_name
    return render_template("post.html", post=post, title=title)


@main.route("/blog/author/<int:author_id>")
def profile(author_id):
    author = Author.query.get(author_id)
    posts = Post.query.filter_by(author_id=author_id).all()
    post_count = Post.query.filter_by(author_id=author_id).count()
    words_total = " ".join([post.content_html for post in posts])
    days_count = (datetime.now() - author.date_join).days
    author_info = {
        "name": author.name,
        "posts": post_count,
        "words": words_total,
        "days": days_count,
        "avatar": author.avatar,
        "intro": author.introduction
    }
    title = u"作者 | " + author.name
    return render_template("profile.html", posts=posts, author_info=author_info, base64=base64, title=title)


@main.route("/blog/tag/<int:tag_id>")
def tags(tag_id):
    tag = Tag.query.get(tag_id)
    posts = Post.query.filter_by(tag_id=tag_id).all()
    title = u"标签 | " + tag.name
    return render_template("tags.html", posts=posts, title=title)


def make_external(url):
    return urljoin(request.url_root, url)


@main.route("/blog/rss.xml")
def rss():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url, url=request.url_root, links=[{"href": url_for('main.rss',   _external=True), "rel": "alternate", "type": "application/atom+xml"}])
    articles = Post.query.order_by(Post.create_time.desc()) \
        .limit(15).all()
    for article in articles:
        feed.add(article.title, content="\n       " + unicode(Markup(article.content_html).replace("\n", "").replace("\r", "").replace("\t", "")),
                 content_type='html',
                 author=Author.query.get(article.author_id).name,
                 url=url_for('main.post', article_name=article.title,
                             _external=True),
                 published=article.create_time,
                 updated=article.modified_time)
    return feed.get_response()


@main.route("/blog/sitemap")
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    # static pages
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            pages.append(
                [rule.rule, ten_days_ago]
            )
    sitemap_xml = render_template(
        'sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

# @main.route("/search", methods=["POST"])
# def search():
#     if not g.search_form.validate_on_submit():
#         return redirect(url_for('main.index'))
#     return redirect(url_for('main.search_results', query=g.search_form.search.data))
#
#
# @main.route("/search_result/<query>")
# def search_results(query):
#     results = Post.query.msearch(query, fields=['title'], limit=20).all()
#     return render_template('search_results.html',
#                            query=query,
#                            results=results)


@main.route("/blog/make_likes/<post_id>", methods=["POST"])
def make_likes(post_id):
    data = request.json
    li = Post.query.get(post_id)
    li.likes = data['like']
    db.session.add(li)
    db.session.commit()
    return json.jsonify({'result': 'ok'})


@main.route("/blog/make_dislikes/<post_id>", methods=["POST"])
def make_dislikes(post_id):
    data = request.json
    li = Post.query.get(post_id)
    li.dislikes = data['dislike']
    db.session.add(li)
    db.session.commit()
    return json.jsonify({'result': 'ok'})


@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
