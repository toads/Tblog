import pytest
from flask_login import current_user


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    auth.login()
    with client:
        client.get('/')
        assert current_user.username == 'test'
        assert current_user.is_authenticated


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Invalid username or password'),
    ('test', 'a', b'Invalid username or password'),
))
def test_login_validate_input(client, username, password, message):
    response = client.post("/auth/login",
                           data={
                               "username": username,
                               "password": password
                           },
                           follow_redirects=True)

    assert message in response.data
