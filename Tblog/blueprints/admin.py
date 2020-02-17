from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from Tblog.extensions import db
from Tblog.models import Admin, Article
from Tblog.utils import redirect_back
from Tblog.forms import SettingForm, SignInForm

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/articles/show', methods=['GET', 'POST'])
@login_required
def switch_show_state():
    aid = request.form.get('aid')

    article = Article.query.get(aid)
    article.show = not article.show
    db.session.add(article)
    db.session.commit()
    return redirect_back()


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about

    return render_template('admin/settings.html', form=form)


@admin_bp.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = SignInForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Password  updated.', 'success')
        return redirect(url_for('blog.index'))
    return render_template('admin/reset_password.html', form=form)


@admin_bp.route('/token', methods=['GET', 'POST'])
@login_required
def get_auth_token():
    admin = Admin.query.first()
    if request.form.get('reset'):
        admin.set_api_key()
        flash("Reset token success!", "info")
    token = admin.api_key
    return render_template('admin/token.html', token=token)


@admin_bp.route('/mange', methods=['GET', 'POST'])
@login_required
def mange():
    settings_form = SettingForm()
    reset_password_form = SignInForm()
    if settings_form.validate_on_submit():
        return settings()
    if reset_password_form.validate_on_submit():
        return reset_password()
    admin = Admin.query.first()
    if request.form.get('reset'):
        admin.set_api_key()
        flash("Reset token success!", "info")
    token = admin.api_key

    settings_form.name.data = current_user.name
    settings_form.blog_title.data = current_user.blog_title
    settings_form.blog_sub_title.data = current_user.blog_sub_title
    settings_form.about.data = current_user.about

    return render_template('admin/mange.html',
                           token=token,
                           settings_form=settings_form,
                           reset_password_form=reset_password_form)
