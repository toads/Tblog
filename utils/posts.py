#!/usr/bin/python3
import argparse
import os
import sys

import requests

url_post = 'http://127.0.0.1:5000/api/articles'
TOKEN = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6InRvYWRzIiwiYXBpX2tleSI6Im9JNDFVNHhSRlBtNFBNeU5sVVQxcU8wQUdHeTdaYUkwIn0.\
        iLReUHrI69D_HunokHV8kB8fWKdSkFfE5DpDev2r48nwSVdVho4pAwvtBnwiaHPZnCwOHyFVYDrY_E95hzvKeg'

update = False
file_list = []
article_path_category_list = []
ready_for_send_articles_list = []

def main(args):
    if category and article and title:
        with open(article) as f:
            body = f.read()
        data = dict(token=token, title=title, body=body, category=category)
        r = requests.post(url_post, json=a)
        print(r.json())
        exit(0)

    articles = requests.get(url_post).json().get('articles')
    # title_category_list = [a['title'],a['category'] for a in articles]
    for root, dirs, files in os.walk(address):
        for name in files:
            print(os.path.join(root, name))
            if name.split('.')[-1] == 'md':
                article_path = os.path.join(root, name)
                category = root.split('/')[-1]
                # if name[:-3],category not in title_category_list or update:
                # article_path_category_list.append(article_path,category)
                # else:
                # print((title, category), 'has already send')

    for article_path, category in article_path_category_list:
        with open(article_path) as f:
            title = article_path('/')[-1][:-3]
            body = f.read()
            data = dict(token=token, title=title, body=body, category=category)
    for a in ready_for_send_articles_list:
        r = requests.post(url_post, json=a)
        print(r.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A Post Tool")

    parser.add_argument(
        'article', default=sys.stdin, type=argparse.FileType('r'),
        help='path/to/the/MarkDown.md')

    parser.add_argument('--update',
                        dest='update',
                        required=False,
                        action='store_true',
                        default=False,
                        help="update all articles")
    parser.add_argument('-c', dest='category', required=False, default='note')
    parser.add_argument('-t', dest='title', required=False)
    parser.add_argument('-T', dest='Token', default=TOKEN, required=False)
    parser.add_argument('-H', dest='host', required=False)
    args = parser.parse_args()
    print(args)
    # main(args)
