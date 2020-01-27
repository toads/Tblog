from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL
from flask_restful import reqparse
from Tblog.models import Category


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(1, 20)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


post_article_parser = reqparse.RequestParser()
post_article_parser.add_argument('token',
                                 type=str,
                                 required=True,
                                 help="Authentication failed")
post_article_parser.add_argument('title', type=str, required=True)
post_article_parser.add_argument('body', type=str, required=True)
post_article_parser.add_argument('category', type=str, required=True)
post_article_parser.add_argument('show', type=bool, default=True)

put_article_parser = reqparse.RequestParser()
put_article_parser.add_argument('token',
                                type=str,
                                required=True,
                                help="Authentication failed")
put_article_parser.add_argument('title', type=str)
put_article_parser.add_argument('body', type=str)
put_article_parser.add_argument('category', type=str)
put_article_parser.add_argument('show', type=bool)

delete_article_parser = reqparse.RequestParser()
delete_article_parser.add_argument('token',
                                   type=str,
                                   required=True,
                                   help="Authentication failed")
