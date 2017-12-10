from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp, DataRequired
from wtforms import ValidationError
# from ..models import Role, User


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
