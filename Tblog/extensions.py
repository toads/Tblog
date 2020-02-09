# -*- coding: utf-8 -*-

from authlib.integrations.flask_client import OAuth
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_httpauth import HTTPBasicAuth
# from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
# ckeditor = CKEditor()
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
# migrate = Migrate()
scheduler = APScheduler()
auth = HTTPBasicAuth()
oauth = OAuth()


@login_manager.user_loader
def load_user(user_id):
    from Tblog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
