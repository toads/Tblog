# -*- coding: utf-8 -*-
import logging
import os
import re
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, render_template, request
from flask_apscheduler import STATE_RUNNING
from flask_wtf.csrf import CSRFError

from Tblog.blueprints.admin import admin_bp
from Tblog.blueprints.api import api_bp
from Tblog.blueprints.auth import auth_bp
from Tblog.blueprints.blog import blog_bp
from Tblog.extensions import (bootstrap, csrf, db, login_manager, mail, moment,
                              oauth, scheduler, toolbar)
from Tblog.models import Admin, Article, Category
from Tblog.settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('Tblog')

    app.config.from_object(config[config_name])
    register_extensions(app)

    oauth.register(
        name='github',
        client_id=app.config.get('GITHUB_CLIENT_ID'),
        client_secret=app.config.get('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )
    register_blueprints(app)
    register_crsf_exclude(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)
    register_commands(app)
    # register_request_handlers(app)
    with app.app_context():
        db.create_all()

    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    toolbar.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    if scheduler.state != STATE_RUNNING:
        scheduler.init_app(app)
        scheduler.start()


def register_logging(app):
    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s')

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/Tblog.log'),
                                       maxBytes=10 * 1024 * 1024,
                                       backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(mailhost=app.config['MAIL_SERVER'],
                               fromaddr=app.config['MAIL_USERNAME'],
                               toaddrs=['ADMIN_EMAIL'],
                               subject='Bluelog Application Error',
                               credentials=(app.config['MAIL_USERNAME'],
                                            app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')


def register_crsf_exclude(app):
    # https://flask-wtf.readthedocs.io/en/stable/csrf.html#exclude-views-from-protection
    # https://security.stackexchange.com/questions/166724/should-i-use-csrf-protection-on-rest-api-endpoints
    csrf.exempt(api_bp)


def register_apis(app):
    app


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Article=Article, Category=Category)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html',
                               description=e.description), 400


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        return dict(admin=admin, categories=categories)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?',
                abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username',
                  prompt=True,
                  help='The username used to login.')
    @click.option('--email',
                  prompt=True,
                  help='The email used to send notice. ')
    @click.option('--password',
                  prompt=True,
                  hide_input=True,
                  confirmation_prompt=True,
                  help='The password used to login.')
    def init(username, email, password):
        """Building Tblog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            click.echo("Email format error")
            return None

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.email = email
            admin.set_password(password)
            admin.ser_api_key()
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(username=username,
                          email=email,
                          blog_title="Toads' Blog",
                          blog_sub_title="Life, Programming, Miscellaneous",
                          name='toads',
                          about='Nothing except you!')
            admin.set_password(password)
            admin.set_api_key()

            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category',
                  default=10,
                  help='Quantity of categories, default is 10.')
    @click.option('--post',
                  default=50,
                  help='Quantity of posts, default is 50.')
    @click.option('--comment',
                  default=500,
                  help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generate fake data."""
        from Tblog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')
