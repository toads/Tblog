# -*- coding: utf-8 -*-
import click
import os


from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from Tblog.blueprints.admin import admin_bp
from Tblog.blueprints.auth import auth_bp
from Tblog.blueprints.blog import blog_bp
from Tblog.blueprints.api import api_bp
from Tblog.extensions import (bootstrap,  csrf, db, toolbar,login_manager,moment,scheduler)
from Tblog.models import Admin, Category, Article
from Tblog.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG','development')
    app = Flask('Tblog')

    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    register_crsf_exclude(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)
    register_commands(app)
    # register_request_handlers(app)
    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    toolbar.init_app(app)
    login_manager.init_app(app) 
    moment.init_app(app)
    scheduler.init_app(app)
    scheduler.start()


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

def register_template_context(app):
    pass


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
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Tblog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title="Toads' Blog",
                blog_sub_title="Life, Programming, Miscellaneous",
                name='Toads',
                about='Nothing except you!'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
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