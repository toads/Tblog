# -*- coding: utf-8 -*-

import base64
from flask_bootstrap import Bootstrap

# from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_apscheduler import APScheduler
from flask_httpauth import HTTPBasicAuth
from authlib.integrations.flask_client import OAuth

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


@login_manager.request_loader
def load_user_from_request(request):
    from Tblog.models import Admin
    api_key = request.args.get('api_key')
    if api_key:
        user = Admin.query.filter_by(api_key=api_key).first()
        if user:
            return user

    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = Admin.query.filter_by(api_key=api_key).first()
        if user:
            return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
