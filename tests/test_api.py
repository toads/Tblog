from flask import json, jsonify,url_for
import pytest

def test_get_token(auth,client):
    auth.login('test','test')
    resp = client.get('/auth/test/token?json=1')
    assert resp.data
    data = json.loads(resp.data)
    assert data
    token = data.get('token')
    assert token
    return token


def test_token(auth, client):
    token = test_get_token(auth, client)
    
    title = "test_put_article_title_token"

    data = dict(
        token = token,
        title = title,
    )

    resp = client.put('/api/articles/{article_id}'.format(article_id=1))
    data = json.loads(resp.data)
    assert not data.get('article_id')
    assert data.get('message')
    assert data.get('message').get('token') == 'Authentication failed'
    
def test_post_article(auth, client):
    token = test_get_token(auth,client)
    print(token)
    auth.logout()
    title = "how to write blog"

    body = """
     # Test
     Test case 1
     ~~~~~~~~~~~~~~~~~~~~~~
     print ("hello world!")
     ~~~~~~~~~~~~~~~~~~~~~~
     2. Test case 2
     ##  Secondary directory
     ### Third-level directory
     ** Emphasis **    """
    category = 'test_category'

    data = dict(
        token = token,
        title = title,
        body = body,
        category = category
    )

    resp = client.post('/api/articles',json=data)
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
    token = test_get_token(auth,client)
    title = "test_put_article_title"
    category = 'test_category_for_put'
    data = dict(
        token = token,
        title = title,
        category = category
    )

    resp = client.put('/api/articles/{article_id}'.format(article_id=1),json=data)
    data = json.loads(resp.data)
    print(token)
    assert data.get('article_id') == 1
    
    resp = client.get('/articles/{article_id}'.format(article_id=1))

    assert resp.status_code == 200
    assert b'test_put_article_title' in resp.data 
    assert b'test_category_for_put' in resp.data


# @pytest.mark.skip(reason="no way of currently testing this")
def test_delete_article(auth, client):
    test_put_article(auth,client)
    token = test_get_token(auth,client)
    print(token)
    auth.logout()

    token_data = dict(
        token = token,
    )
    resp = client.delete('/api/articles/{article_id}'.format(article_id=1),json=token_data)
    data = json.loads(resp.data)
    assert data.get('message') ==  "article delete success"
    resp = client.delete('/api/articles/{article_id}'.format(article_id=1),json=token_data)
    data = json.loads(resp.data)
    assert data.get('message') == "article has been delete"

    