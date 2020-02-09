import pytest
from Tblog import create_app
from Tblog.models import Admin, Category
from Tblog.extensions import db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app("testing")
    app.config['SECRET_KEY'] = 'testing_key'
    # create the database and load test data
    with app.app_context():

        db.drop_all()
        db.create_all()
        admin = Admin(username='testuser',
                      blog_title="Tests Blog",
                      blog_sub_title="Life, Programming, Miscellaneous",
                      name='Tests',
                      about='Nothing except you!')
        admin.set_password('testpassword')
        db.session.add(admin)
        category = Category.query.first()
        category = Category(name='Default')
        db.session.add(category)
        db.session.commit()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_empty_db(client):
    """Start with a blank database."""
    rv = client.get('/')
    assert b'No entries here so far' in rv.data


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="testuser", password="testpassword"):
        return self._client.post("/auth/login",
                                 data={
                                     "username": username,
                                     "password": password
                                 })

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
