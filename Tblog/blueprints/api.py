from flask import Blueprint, abort, jsonify, make_response, g
from Tblog.models import Admin, Article, Category
from Tblog.extensions import db, auth

from flask_restful import Resource, Api
from Tblog.forms import (put_article_parser, list_article_id_parser)
api_bp = Blueprint('api', __name__)

api = Api(api_bp, catch_all_404s=True)


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = Admin.verify_api_key(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = Admin.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.username = user.username
    return True


@auth.error_handler
def unauthorized():
    # TODO: add fail2ban function
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def check_category(category):
    if not category:
        return None
    category_item = Category.query.filter_by(name=category).first()
    if category_item is None:
        category_item = Category(name=category)
        db.session.add(category_item)
        db.session.commit()
    return category_item


def update_article(id=-1):
    args = put_article_parser.parse_args()
    category_item = check_category(category=args.category)
    article = Article.query.get(id)
    if not article:
        article = Article()
        if id != -1:
            article.id = id
        article.author = g.username

    if article.author != g.username:
        abort(403, "Only the own can edit this article")

    if args.title:
        article.title = args.title
    if args.body:
        article.body = args.body
    if args.category:
        article.category = category_item
    if type(args.show) is bool:
        article.show = args.show
    article.author = g.username
    db.session.add(article)
    db.session.commit()
    return article


def delete_article(id):
    admin = Admin.query.first()
    article = Article.query.filter_by(id=id)
    article_item = article.first()
    if article_item:
        if article_item.author != g.username or admin.username != g.username:
            abort(403, "Only the admin or owner can delete the article")
        article.delete()
        db.session.commit()
        return id
    else:
        abort(400, "article has been delete")


class Token(Resource):
    @auth.login_required
    def get(self):
        token = Admin.query.filter_by(username=g.username).first().api_key
        return jsonify({'username': g.username, 'token': token})


class ArticleItem(Resource):
    def get(self, id):
        post = Article.query.get(id)
        if post:
            return post.to_json()
        return

    @auth.login_required
    def put(self, id):
        article = update_article(id)
        return {"article_id": article.id}

    @auth.login_required
    def delete(self, id):
        id = delete_article(id)
        return {"article_id": id}


class ArticlesList(Resource):
    def get(self):
        articles = Article.query.filter_by(show=True).all()
        articles_dict = dict(articles=[])
        for article in articles:
            articles_dict['articles'].append(article.to_json(summary=True))
        return articles_dict

    @auth.login_required
    def post(self):
        article = update_article()
        return {"article_id": article.id}

    @auth.login_required
    def put(self):
        args = list_article_id_parser.parse_args()
        article = update_article(args.id)
        return {"article_id": article.id}

    @auth.login_required
    def delete(self):
        args = list_article_id_parser.parse_args()
        id = delete_article(args.id)
        return {"article_id": id}


api.add_resource(ArticlesList, '/articles')
api.add_resource(ArticleItem, '/articles/<int:id>')
api.add_resource(Token, '/token')
