from flask_restful import reqparse
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(1, 20)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title',
                             validators=[DataRequired(),
                                         Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title',
                                 validators=[DataRequired(),
                                             Length(1, 100)])
    about = TextAreaField('About')
    submit = SubmitField()


class SignInForm(FlaskForm):
    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(1, 128)
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField()


put_article_parser = reqparse.RequestParser()
put_article_parser.add_argument('title', type=str)
put_article_parser.add_argument('body', type=str)
put_article_parser.add_argument('category', type=str)
put_article_parser.add_argument('show', type=bool)

list_article_id_parser = reqparse.RequestParser()
list_article_id_parser.add_argument('id', type=int)
