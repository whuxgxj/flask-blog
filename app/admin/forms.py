#-*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateTimeField, BooleanField, PasswordField, SelectField, FileField
from wtforms.validators import Required, Length, Email, Optional, EqualTo
from flask_wtf.file import FileAllowed, FileRequired


class LoginForm(FlaskForm):
    username = StringField('', validators=[
        Required(), Length(1, 64)], render_kw={"placeholder": "username"})
    password = PasswordField('', validators=[Required()], render_kw={
                             "placeholder": "password"})
    remember_me = BooleanField(u"记住")
    submit = SubmitField(u"登录")


class RegistrationForm(FlaskForm):
    email = StringField("", validators=[Required(), Length(1, 64), Email(
        u'请输入一个合法的邮箱')], render_kw={"placeholder": "email"})
    username = StringField("", validators=[Required(), Length(
        1, 64)], render_kw={"placeholder": "username"})
    password = PasswordField('', validators=[Required()], render_kw={
        "placeholder": "password"})
    repassword = PasswordField(
        '', validators=[Required(), EqualTo('password', message=u"您输入的密码不一致")], render_kw={"placeholder": "reinput your password"})
    submit = SubmitField(u"注册")


class EntryForm(FlaskForm):
    title = StringField(u"标&emsp;题", validators=[Required()])
    subtitle = StringField(u"副标题", validators=[Optional()])
    author = StringField(u"作&emsp;者", validators=[Required()])
    tag = StringField(u"标&emsp;签", validators=[Required()])
    category = SelectField(
        u"目&emsp;录", choices=[])
    abstract = TextAreaField(u"摘&emsp;要", validators=[
                             Required(), Length(1, 250, message=u"摘要文本应保持在250字以内")], render_kw={"rows": 10})
    body = TextAreaField(u"正&emsp;文", validators=[
                         Required()])
    submit = SubmitField(u"提交")


class UserForm(FlaskForm):
    email = StringField(u"邮箱", validators=[Required(), Length(1, 64), Email(
        u'请输入一个合法的邮箱')], render_kw={"placeholder": "email"})
    username = StringField(u"用户名", validators=[Required(), Length(
        1, 64)], render_kw={"placeholder": "username"})
    password = PasswordField(u'密码', validators=[Required()], render_kw={
        "placeholder": "password"})
    repassword = PasswordField(
        u'确认密码', validators=[Required(), EqualTo('password', message=u"您输入的密码不一致")], render_kw={"placeholder": "reinput your password"})
    avatar = FileField(u"头像图片", validators=[FileRequired()])
    submit = SubmitField(u"提交")


class AuthorForm(FlaskForm):
    email = StringField(u"邮箱", validators=[Required(), Length(1, 64), Email(
        u'请输入一个合法的邮箱')], render_kw={"placeholder": "email"})
    name = StringField(u"昵称", validators=[Required(), Length(
        1, 64)], render_kw={"placeholder": "username"})
    avatar = FileField(u"头像图片", validators=[FileRequired()])
    intro = TextAreaField(
        u"简介", validators=[Required(), Length(1, 150, message="简介不超过150字")])
    submit = SubmitField(u"提交")
