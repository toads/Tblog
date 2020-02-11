from flask import json
import base64


def test_get_token_by_api(auth, client):

    valid_credentials = base64.b64encode(b'testuser:testpassword').decode(
        'utf-8')
    response = client.get(
        '/api/token', headers={'Authorization': 'Basic ' + valid_credentials})
    assert response.status == '200 OK'
    assert json.loads(response.data).get('token')
    return json.loads(response.data).get('token')


def test_token(auth, client):
    token = test_get_token_by_api(auth, client)

    title = "test_put_article_title_token"

    data = dict(
        token=token,
        title=title,
    )

    resp = client.put('/api/articles/{article_id}'.format(article_id=1))
    data = json.loads(resp.data)
    assert not data.get('article_id')
    assert data.get('error')
    assert data.get('error') == 'Unauthorized access'


def test_post_article(auth, client):
    token = test_get_token_by_api(auth, client)
    auth.logout()
    title = "how to write blog"

    body = """
     # Test
     Test case 1
     ~~~~~~~~~~~~~~~~~~~~~~
     print ("hello world!")
     ~~~~~~~~~~~~~~~~~~~~~~`
     2. Test case 2
     ##  Secondary directory
     ### Third-level directory
     ** Emphasis **    """
    category = 'test_category'

    data = dict(title=title, body=body, category=category, show=True)
    valid_credentials = base64.b64encode(
        (token + ": ").encode('utf-8')).decode('utf-8')

    resp = client.post('/api/articles',
                       json=data,
                       headers={'Authorization': 'Basic ' + valid_credentials})
    data = json.loads(resp.data)
    assert data.get('article_id')
    article_id = data.get('article_id')
    resp = client.get('/articles/{article_id}'.format(article_id=article_id))
    assert resp.status_code == 200
    assert b'print ("hello world!")' in resp.data
    assert b'Test case 2' in resp.data
    assert b'test_category' in resp.data
    assert b"how to write blog" in resp.data


# @pytest.mark.skip(reason="no way of currently testing this")
def test_put_article(auth, client):
    title = "test_put_article_title"
    category = 'test_category_for_put'
    data = dict(title=title, category=category)
    valid_credentials = base64.b64encode(b'testuser:testpassword').decode(
        'utf-8')

    resp = client.put('/api/articles/{article_id}'.format(article_id=1),
                      json=data,
                      headers={'Authorization': 'Basic ' + valid_credentials})
    data = json.loads(resp.data)
    assert data.get('article_id') == 1

    resp = client.get('/articles/{article_id}'.format(article_id=1))

    assert resp.status_code == 200
    assert b'test_put_article_title' in resp.data
    assert b'test_category_for_put' in resp.data


# @pytest.mark.skip(reason="no way of currently testing this")
def test_delete_article(auth, client):
    test_put_article(auth, client)
    auth.logout()

    valid_credentials = base64.b64encode(b'testuser:testpassword').decode(
        'utf-8')

    resp = client.delete(
        '/api/articles/{article_id}'.format(article_id=1),
        headers={'Authorization': 'Basic ' + valid_credentials})
    data = json.loads(resp.data)
    assert resp.status == '200 OK'
    assert data.get('article_id') == 1
    resp = client.delete(
        '/api/articles/{article_id}'.format(article_id=1),
        headers={'Authorization': 'Basic ' + valid_credentials})
    data = json.loads(resp.data)
    assert data.get('message') == "article has been delete"
