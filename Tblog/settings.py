import os
import re
import sys
import logging
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdfasdfasdfasdfey')
    MAIL_HOST = os.getenv('EMAIL_HOST', 'imap.gmail.com')
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME', 'user@example.com')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'password')

    MAIL_SERVER = os.getenv('EMAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = ('Tblog Admin', MAIL_USERNAME)
    EMAIL_SOURCE = os.getenv('EMAIL_SOURCE')
    if not EMAIL_SOURCE:
        logging.warning("EMAIL_SOURCE LIST NOT SET")
        EMAIL_SOURCE = ''

    MAIL_SOURCE = re.findall(
        r'\s*(?:([a-zA-Z0-9_.]+@\w+\.[a-zA-Z]+?)(?:,|，){0,1}(?:\s+))\s*',
        EMAIL_SOURCE + ' ',
        flags=re.ASCII)
    TBLOG_ADMIN_MAIL = os.getenv('TBLOG_ADMIN_MAIL')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        logging.warning("GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET NOT SET")

    SCHEDULER_API_ENABLE = True
    JOBS = [{
        'id': 'auto_check_email',
        'func': 'Tblog.emails:check_email',
        'args': None,
        'trigger': 'interval',
        'seconds': 10
    }]


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'db/data-dev.db')
    JOBS = [{
        'id': 'auto_check_email',
        'func': 'Tblog.emails:check_email',
        'args': None,
        'trigger': 'interval',
        'seconds': 1000
    }]


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', prefix + os.path.join(basedir, 'db/data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
