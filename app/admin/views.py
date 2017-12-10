#-*-coding:utf-8-*-
from flask import render_template, redirect, request, url_for, flash, g
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import admin
from .. import db, app
from ..models import User, Post, Author, Tag, Category
# from ..email import send_email
from .forms import LoginForm, EntryForm, RegistrationForm, AuthorForm, UserForm
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import base64


@admin.before_app_request
def before_request():
    if not User.query.all():
        admin = User(username="rudy", password="admin-rudy",
                     email="tomorrow2future@gmail.com")
        db.session.add(admin)
        db.session.commit()
    g.base64 = base64


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('admin.index'))
        flash('用户名或密码错误')
    return render_template('admin/login.html', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('admin.index'))


@admin.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        return redirect(url_for('admin.login'))
    return render_template('admin/register.html', form=form)


@admin.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("admin/base.html")


@admin.route("/entry", methods=["GET", "POST"])
@login_required
def entry():
    return render_template("admin/entry.html", Post=Post, Author=Author, Category=Category)


@admin.route("/entry/add", methods=["GET", "POST"])
@login_required
def add_entry():
    form = EntryForm()
    cat_choices = [(str(cat.id), cat.name) for cat in Category.query.all()]
    form.category.choices = cat_choices
    if form.validate_on_submit():
        if Author.query.filter_by(name=form.author.data).first() == None:
            author = Author(name=form.author.data)
            db.session.add(author)
        if Tag.query.filter_by(name=form.tag.data).first() == None:
            tag = Tag(name=form.tag.data)
            db.session.add(tag)
        post = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author_id=Author.query.filter_by(
                name=form.author.data).first().id,
            tag_id=Tag.query.filter_by(name=form.tag.data).first().id,
            content_md=form.body.data,
            content_html=Post.generate_markdown(form.body.data),
            abstract=form.abstract.data,
            category_id=int(form.category.data),
            modified_time=datetime.utcnow()
        )
        db.session.add(post)
        flash(u'您所编辑的文章已提交')
        return redirect(url_for("admin.entry"))
    return render_template("admin/add_entry.html", form=form)


@admin.route("/entry/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_entry(post_id):
    entry = Post.query.get_or_404(post_id)
    form = EntryForm(obj=entry)
    cat_choices = [(str(cat.id), cat.name) for cat in Category.query.all()]
    form.category.choices = cat_choices
    if form.validate_on_submit():
        if Author.query.filter_by(name=form.author.data).first() == None:
            author = Author(name=form.author.data)
            db.session.add(author)
        if Tag.query.filter_by(name=form.tag.data).first() == None:
            tag = Tag(name=form.tag.data)
            db.session.add(tag)
        entry.title = form.title.data
        entry.subtitle = form.subtitle.data
        entry.author_id = Author.query.filter_by(
            name=form.author.data).first().id
        entry.tag_id = Tag.query.filter_by(name=form.tag.data).first().id
        entry.content_md = form.body.data
        entry.content_html = Post.generate_markdown(form.body.data)
        entry.abstract = form.abstract.data
        entry.category_id = int(form.category.data)
        entry.modified_time = datetime.utcnow()
        db.session.commit()
        flash(u"您刚刚成功编辑了您的文章")
        return redirect(url_for("admin.entry"))
    form.title.data = entry.title
    form.subtitle.data = entry.subtitle
    form.author.data = Author.query.get(entry.author_id).name
    form.tag.data = Tag.query.get(entry.tag_id).name
    form.body.data = entry.content_md
    form.abstract.data = entry.abstract
    form.category.data = Category.query.get(entry.category_id).name
    return render_template("admin/add_entry.html", form=form)


@admin.route("/entry/delete/<int:post_id>", methods=["GET", "POST"])
@login_required
def delete_entry(post_id):
    entry = Post.query.get_or_404(post_id)
    db.session.delete(entry)
    db.session.commit()
    flash(u"you have successfully delete a post entry")
    return redirect(url_for('admin.entry'))

    # @auth.route('/unconfirmed')
    # def unconfirmed():
    #     if current_user.is_anonymous or current_user.confirmed:
    #         return redirect(url_for('admin.index'))
    #     return render_template('admin.unconfirmed.html')


@admin.route("/user", methods=["GET", "POST"])
@login_required
def user():
    return render_template("admin/user.html", User=User, base64=base64)


@admin.route("/user/add", methods=["GET", "POST"])
@login_required
def add_user():
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        f = request.files.get("avatar").read()
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            avatar=f
        )
        db.session.add(user)
        db.session.commit()
        flash(u"您已添加一位用户")
        return redirect(url_for('admin.user'))
    return render_template("admin/add_user.html", form=form)


@admin.route("/user/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        user.avatar = request.files.get("avatar").read()
        db.session.add(user)
        db.session.commit()
        flash(u"you have modified your user profile!")
        return redirect(url_for('admin.user'))
    form.username.data = user.username
    form.email.data = user.email
    form.password.data = user.password_hash
    form.avatar.data = user.avatar
    return render_template("admin/add_user.html", form=form)


@admin.route("/user/delete/<int:user_id>", methods=["GET", "POST", "DELETE"])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(u"you have deleted one user info!")
    return redirect(url_for('admin.user'))


@admin.route("/author", methods=["GET", "POST"])
@login_required
def author():
    return render_template("admin/author.html", Author=Author, base64=base64)


@admin.route("/author/add", methods=["GET", "POST"])
@login_required
def add_author():
    form = AuthorForm()
    if request.method == 'POST' and form.validate_on_submit():
        f = request.files.get("avatar").read()
        author = Author(
            name=form.name.data,
            email=form.email.data,
            avatar=f,
            introduction=form.intro.data
        )
        db.session.add(author)
        db.session.commit()
        flash(u"您已添加一位作者")
        return redirect(url_for('admin.author'))
    return render_template("admin/add_author.html", form=form)


@admin.route("/author/edit/<int:author_id>", methods=["GET", "POST"])
@login_required
def edit_author(author_id):
    author = Author.query.get_or_404(author_id)
    form = AuthorForm(obj=author)
    if request.method == 'POST' and form.validate_on_submit():
        author.name = form.name.data
        author.email = form.email.data
        author.introduction = form.intro.data
        author.avatar = request.files.get("avatar").read()
        db.session.add(author)
        db.session.commit()
        flash(u"you have modified your author profile!")
        return redirect(url_for('admin.author'))
    form.name.data = author.name
    form.email.data = author.email
    form.intro.data = author.introduction
    return render_template("admin/add_author.html", form=form)


@admin.route("/author/delete/<int:author_id>", methods=["GET", "POST", "DELETE"])
@login_required
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash(u"you have deleted one author info!")
    return redirect(url_for('admin.author'))


# @auth.route('/confirm/<token>')
# @login_required
# def confirm(token):
#     if current_user.confirmed:
#         return redirect(url_for('admin.index'))
#     if current_user.confirm(token):
#         flash('You have confirmed your account. Thanks!')
#     else:
#         flash('The confirmation link is invalid or has expired.')
#     return redirect(url_for('admin.index'))


# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
#     token = current_user.generate_confirmation_token()
#     send_email(current_user.email, 'Confirm Your Account',
#                'auth/email/confirm', user=current_user, token=token)
#     flash('A new confirmation email has been sent to you by email.')
#     return redirect(url_for('admin.index'))


# @auth.route('/change-password', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     form = ChangePasswordForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.old_password.data):
#             current_user.password = form.password.data
#             db.session.add(current_user)
#             flash('Your password has been updated.')
#             return redirect(url_for('admin.index'))
#         else:
#             flash('Invalid password.')
#     return render_template("admin/change_password.html", form=form)


# @auth.route('/reset', methods=['GET', 'POST'])
# def password_reset_request():
#     if not current_user.is_anonymous:
#         return redirect(url_for('admin.index'))
#     form = PasswordResetRequestForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             token = user.generate_reset_token()
#             send_email(user.email, 'Reset Your Password',
#                        'admin/email/reset_password',
#                        user=user, token=token,
#                        next=request.args.get('next'))
#         flash('An email with instructions to reset your password has been '
#               'sent to you.')
#         return redirect(url_for('auth.login'))
#     return render_template('admin/reset_password.html', form=form)

#
# @auth.route('/reset/<token>', methods=['GET', 'POST'])
# def password_reset(token):
#     if not current_user.is_anonymous:
#         return redirect(url_for('admin.index'))
#     form = PasswordResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user is None:
#             return redirect(url_for('admin.index'))
#         if user.reset_password(token, form.password.data):
#             flash('Your password has been updated.')
#             return redirect(url_for('admin.login'))
#         else:
#             return redirect(url_for('main.index'))
#     return render_template('admin/reset_password.html', form=form)


# @auth.route('/change-email', methods=['GET', 'POST'])
# @login_required
# def change_email_request():
#     form = ChangeEmailForm()
#     if form.validate_on_submit():
#         if current_user.verify_password(form.password.data):
#             new_email = form.email.data
#             token = current_user.generate_email_change_token(new_email)
#             send_email(new_email, 'Confirm your email address',
#                        'admin/email/change_email',
#                        user=current_user, token=token)
#             flash('An email with instructions to confirm your new email '
#                   'address has been sent to you.')
#             return redirect(url_for('admin.index'))
#         else:
#             flash('Invalid email or password.')
#     return render_template("admin/change_email.html", form=form)


# @auth.route('/change-email/<token>')
# @login_required
# def change_email(token):
#     if current_user.change_email(token):
#         flash('Your email address has been updated.')
#     else:
#         flash('Invalid request.')
#     return redirect(url_for('admin.index'))
