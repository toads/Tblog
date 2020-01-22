from flask import Blueprint,current_app, redirect,render_template,flash,url_for,jsonify,abort
from flask_login import login_user, logout_user, login_required, current_user

from Tblog.forms import LoginForm
from Tblog.models import Admin
from Tblog.utils import redirect_back
from itsdangerous import JSONWebSignatureSerializer as Serializer

auth_bp = Blueprint('auth', __name__)




@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if admin.verify_password(username, password):
                login_user(admin, remember)
                flash('Welcome back.', 'info')
                return redirect_back()
            flash('Invalid username or password.', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()

 
@auth_bp.route('/users/<string:username>/token',methods=['GET'])
@login_required
def get_auth_token(username):
    if username!=(current_user.username.lower()):
        print(current_user.username)
        abort(400)
    admin = Admin.query.filter_by(username=username).first()
    s = Serializer(current_app.config['SECRET_KEY'])
    token = s.dumps({'username':username,'api_key':admin.api_key})
    return render_template('auth/token.html',token=token.decode('utf-8'))

