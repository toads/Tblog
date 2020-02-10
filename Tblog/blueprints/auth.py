from flask import (Blueprint, flash, jsonify, redirect, session, json,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from authlib.common.errors import AuthlibBaseError
from Tblog.extensions import oauth, db
from Tblog.forms import LoginForm
from Tblog.models import Admin
from Tblog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        session['username'] = current_user.username
        return redirect(url_for('blog.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if admin.verify_password(password):
                login_user(admin, remember)
                session['username'] = username
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('Invalid username or password.', 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/oauth/github')
def login_github():
    github = oauth.create_client('github')
    return github.authorize_redirect(url_for('auth.authorized',
                                             _external=True))


@auth_bp.route('/logout')
def logout():
    logout_user()
    session.pop('github_token', None)
    return redirect_back()


@auth_bp.route('/login/authorized')
def authorized():
    try:
        oauth.github.authorize_access_token()
    except AuthlibBaseError as e:
        flash(str(e), 'warning')
        return redirect(url_for('auth.login'))
    resp = oauth.github.get('user/emails')

    username = oauth.github.get('user').json().get('login')

    emails = json.loads(resp.text)
    primary_email = [email['email'] for email in emails if email['primary']]
    if not primary_email:
        flash("Plz check your primary email is right")
        return redirect(url_for('auth.login'))
    primary_email = primary_email[0]
    if Admin.query.first() is None:
        admin = Admin(username=username, email=primary_email)
        admin.set_api_key()
        admin.set_password(admin.api_key)
        db.session.add(admin)
        db.session.commit()
        login_user(admin, remember=True)
        flash(
            "Welcome to register, your username is {username} and password "
            "is {password} can log in through GitHub or username&password "
            "in the future".format(username=username, password=admin.api_key),
            "info")
        return redirect_back()

    admin = Admin.query.filter_by(email=primary_email).first()
    session['username'] = username
    if admin:
        login_user(admin, remember=True)
        flash("Welcome come back", 'info')
        return redirect_back()
    else:
        flash("Welcome to tblog {username}".format(username=username), "info")
        return redirect_back()


@auth_bp.route('/token', methods=['GET'])
@login_required
def get_auth_token(reset=False):
    admin = Admin.query.first()
    if request.args.get('reset'):
        admin.set_api_key()
        flash("Reset token success!", "info")
    token = admin.api_key
    if request.args.get('json'):
        return jsonify({'username': current_user.username, 'token': token})
    return render_template('auth/token.html', token=token)
