def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Log Out" not in response.data

    auth.login()
    response = client.get('/')
    assert b"Log In" not in response.data
    assert b'Log Out' in response.data
    # assert b"Tests Blog" in response.data # excpet error
    assert b'Token' in response.data
    assert b'About Me' in response.data

    auth.logout()
    response = client.get('/')
    assert b"Log In" in response.data
    assert b'Log Out' not in response.data
    # assert b"Tests Blog" in response.data # excpet error
    assert b'Token' not in response.data
    assert b'About Me' in response.data


def test_about(client):
    response = client.get('/about')
    print(response.data)
    assert b"Life, Programming, Miscellaneous" in response.data
    assert b"Tests" in response.data


def test_token(client, auth):
    response = client.get('/admin/token')
    assert response.status_code == 302
    assert b"Redirecting" in response.data
    auth.login()
    response = client.get('/admin/token')
    assert b"Current user: test" in response.data
