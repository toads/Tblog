#!/usr/bin/python3
import requests
import os
import sys
import argparse
import re
url_post = 'http://127.0.0.1:5000/api/articles'
token = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6InRvYWRzIiwiYXBpX2tleSI6Im9JNDFVNHhSRlBtNFBNeU5sVVQxcU8wQUdHeTdaYUkwIn0.\
        iLReUHrI69D_HunokHV8kB8fWKdSkFfE5DpDev2r48nwSVdVho4pAwvtBnwiaHPZnCwOHyFVYDrY_E95hzvKeg'
update = False
file_list = []
article_path_category_list = []
ready_for_send_articles_list = []

def usage():
    print(sys.argv[0],'[path_to_blog_file]','[option args]')
    exit(255)


def main(address,update=False,category=None,article=None,title=None, token_=None,url=None):
    if len(sys.argv) == 1:
        usage()
    if token_:
        token = token_
    if url:
        url_post = url
    if category and article and title:
        with open(article) as f:
            body = f.read()
        data = dict(
                token = token,
                title = title,
                body = body,
                category = category
            )
        r = requests.post(url_post,json=a)
        print(r.json())
        exit(0)
    
    articles = requests.get(url_post).json().get('articles')
    title_category_list = [a['title'],a['category'] for a in articles]
    for root,dirs,files in os.walk(address):
        for name in files:
            print(os.path.join(root, name))
            if name.split('.')[-1]=='md':
                article_path = os.path.join(root, name)
                category = root.split('/')[-1]
                if name[:-3],category not in title_category_list or update:
                    article_path_category_list.append(article_path,category)
                else:
                    print((title, category), 'has already send')


    for article_path,category in article_path_category_list:
        with open(article_path) as f:
            title= article_path('/')[-1][:-3]
            body = f.read()
            data = dict(
                token = token,
                title = title,
                body = body,
                category = category
            )
    for a in ready_for_send_articles_list:
        r = requests.post(url_post,json=a)
        print(r.text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest = "address", help = "path to blog file")
    parser.add_argument(dest = 'update', required=False, default=False, help="update all articles")
    parser.add_argument('-c',dest='category',required=False)
    parser.add_argument('-a',dest='article', required=False)
    parser.add_argument('-t',dest='title', required=False)
    parser.add_argument('-T',dest='Token', required=False)
    parser.add_argument('-u',dest='url', required=False)
    args = parser.parse_args()
    main(args.address,args.update,args.category,args.article,args.title)