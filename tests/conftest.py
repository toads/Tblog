import os
import tempfile

import pytest
from Tblog import create_app
from Tblog.extensions import db
@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})
    
    # create the database and load test data
    with app.app_context():
        db.create_all()
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
        category = Category(name='Default')
        db.session.add(category)
        db.session.commit()
        yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

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

    def login(self, username="admin", password="admin"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)