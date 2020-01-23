import os
import sys
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdfasdfasdfasdfey')
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'imap.gmail.com')
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', 'user@example.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'password')
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SCHEDULER_API_ENABLE = True
    JOBS = [
        {
            'id': 'auto_check_email',
            'func': 'Tblog.emails:check_email', 
            'args': None,
            'trigger': 'interval',
            'seconds': 600
        }
    ]
    


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}