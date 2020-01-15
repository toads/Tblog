# -*- coding: utf-8 -*-
import click
import os


from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

# from flask_bootstrap import Bootstrap
from Tblog.blueprints.admin import admin_bp
from Tblog.blueprints.auth import auth_bp
from Tblog.blueprints.blog import blog_bp
from Tblog.extensions import (bootstrap,  csrf, db, toolbar,login_manager,moment,api)

from Tblog.models import Admin, Category, Post
from Tblog.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG','development')
    app = Flask('Tblog')

    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
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
    api.init_app(app)

def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category)

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
